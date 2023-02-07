from cgitb import text
import json
import logging
import os
import pandas as pd
import pickle
import time

import bs4
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log")
    ]
)


# Functions to scrape the data
# ============================================

def countries_with_urls():
    # {"name":"Italy","path":"/countries/italy/"},"ITA","IT | ITA | 380","ITA",".it",""
    lines_list = open("country_data_codes.csv", "rt").read().splitlines()[1:]
    # {"name":"Italy","path":"/countries/italy/
    lines_list = [txt.split("\"}", 1)[0] for txt in lines_list]
    countries = {}
    for line in lines_list:
        country_name = line.removeprefix("{\"name\":\"").split("\",", 1)[0]
        if line.find("\"path\":\"") == -1:
            continue
        url = line.split("\"path\":\"", 1)[1]
        url = "https://www.cia.gov/the-world-factbook" + url
        countries[country_name] = {"url": url}
    return countries

def scrape_pages(countries):
    """Scrape the page source from the CIA Factbook"""

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    for country in countries.values():
        try:
            url = country["url"]
            driver.get(url)
            time.sleep(3)
            country["page_source"] = driver.page_source
        except Exception as e:
            logging.warning("Could not scrape the source from {}.\n{}".format(url, e))
    driver.quit()
    return countries


# Functions to parse the data
# ============================================

def parse_countries(countries):
    """Parse the page source for each country."""
    for country in countries.values():
        parse_country(country)
    return countries

def parse_country(country):
    """Given a dictionary of a country with the page source, parse the information."""
    page_source = country.pop("page_source")
    soup = bs4.BeautifulSoup(page_source, "html.parser")
    content = soup.find("div", class_="content-area-content")
    for section in content.children:
        h2_tag = section.find("h2")
        if h2_tag is None:
            continue
        section_name = h2_tag.text
        for h3_tag in section.find_all("h3"):
            parse_h3_tag(h3_tag, section_name, country)

def parse_h3_tag(h3_tag, section_name, country):
    """Parse a bs4 h3 tag
    
    Keyword arguments:
    section_name -- the text of the parent h2 tag (e.g. "Introduction", "Geography")
    country      -- the parent country dictionary to store the parsed information
    """
    column_name = ": ".join([section_name, stripped_tag_text(h3_tag)])
    content_tag = h3_tag.next_sibling

    # Check that the information is actually there
    content_tag_found = True
    if content_tag is None:
        content_tag_found = False
    elif content_tag.text.strip() == "":
        content_tag_found = False
        
    if not content_tag_found:
        logging.warning("Information not found for section \"{}\" in \"{}\".".format(h3_tag.text, country["url"]))
        print("WARNING You might want to check section \"{}\" at \"{}\", I did not find anything.".format(h3_tag.text, country["url"]))
        return
    parse_content_tag(content_tag, column_name , country)

def parse_content_tag(content_tag, column_name, country):
    """Parse information from `<p>` and `<strong>` tags

    Keyword arguments:
    content_tag -- a bs4 tag between header tags (`<h2>`, `<h3>`)
    column_name -- name of the column for the information in the content_tag,
                   based on the the parent `<h2>` and `<h3>` tags
    country     -- the parent country dictionary to store the parsed information
    """

    # If `content_tag` is a bs4 Tag, then it could contain `strong`` tags.
    # If not, it is probably a bs4 NavigableString and the list of `strong` tags is empty.
    if type(content_tag) is bs4.element.Tag:
        strong_tags = content_tag.find_all("strong")
    else:
        strong_tags = []
    
    # If there are `strong` tags, each of them gets a separate column.
    # This case probably deserves its own function.
    if len(strong_tags) > 0:
        parse_strong_tags(strong_tags, content_tag, column_name, country)
    # If there are no `strong` tags, then the whole section's text is taken
    elif content_tag.text != "":
        country[column_name] = content_tag.text
    elif content_tag.next_sibling is None:
        logging.warning("I could not find a paragraph for section \"{}\" on \"{}\".".format(section_name, country["url"]))
    else:
        country[column_name] = content_tag.next_sibling.text

def parse_strong_tags(strong_tags, content_tag, column_name, country):
    """Parse information from `<strong>` tags

    E.g. "total", "land", "water" in *Geography* > *Area*

    Keyword arguments:
    strong_tags -- list of bs4 `<strong>` tags from a section
    content_tag -- parent bs4 tag
    column_name -- name of the column for the information in the content_tag,
                   based on the the parent `<h2>` and `<h3>` tags
    country     -- the parent country dictionary to store the parsed information
    """
    # There might be information before the first `strong` tag.
    # If so, it gets its own column.
    if not content_tag.text.startswith(strong_tags[0].text):
        country[column_name] = content_tag.text.split(strong_tags[0].text, 1)[0]

    # Each `strong` tag gets its own column
    last_strong_tag = None
    for i in range(len(strong_tags) - 1):

        if strong_tags[i].text == "":
            continue
        column_name2 = " - ".join([column_name, stripped_tag_text(strong_tags[i])])
        txt = content_tag.text
        txt = txt.split(strong_tags[i].text, 1)[1]
        # This is to handle a stupid case of `<strong><br></strong>` in the source.
        # If no proper `strong` tag is left, then that is the last tag of the section
        # and is handeled separetely.
        # I feel like there is a smarter way to do this.
        next_non_empty_strong_tag = None
        for j in range(i+1, len(strong_tags)):
            if stripped_tag_text(strong_tags[j]) != "":
                next_non_empty_strong_tag = strong_tags[j]
                break
        if next_non_empty_strong_tag is None:
            last_strong_tag = strong_tags[i]
            break
        else:
            txt = txt.split(strong_tags[j].text, 1)[0]
        country[column_name2] = txt.strip()

    if last_strong_tag is None:
        last_strong_tag = strong_tags[-1]
    if last_strong_tag.text.strip() != "":
        column_name2 = " - ".join([column_name, stripped_tag_text(last_strong_tag)])
        txt = content_tag.text
        txt = txt.split(last_strong_tag.text, 1)[1]
        # Find the tag starting the next subsection, which will start with a `h2` tag.
        # If none is found, just keep whatever is left.
        next_subsection_tag = None
        for tag in last_strong_tag.next_siblings:
            if repr(tag).startswith("<h2"):
                next_subsection_tag = tag
                break
        if next_subsection_tag is not None:
            txt.split(next_subsection_tag.text)[0]
        country[column_name2] = txt.strip()

def stripped_tag_text(tag):
    """Given a bs4 tag, return the text stripped of irrelevant characters."""
    return tag.text.strip(":- \u00a0\u2014")


# Functions to export the data
# ============================================

def export_countries_urls(countries):
    """Export the countries with link to the source as markdown."""
    lines = ["- [{}]({})".format(country_name, country["url"])
             for country_name, country in countries.items()]
    open("countries_urls.md", "wt").write("\n".join(lines))

def export_list_of_columns(countries):
    """Export a list of all columns as markdown."""
    columns = []
    for country in countries.values():
        columns = columns + list(country.keys())
    columns = list(dict.fromkeys(columns))
    columns.sort()
    columns = ["- " + c for c in columns]
    open("columns.md", "wt").write("\n".join(columns))


if __name__ == "__main__":
    pickle_name = "countries_with_page_source.pickle" 
    if os.path.exists(pickle_name):
        countries = pickle.load(open(pickle_name, "rb"))
    else:
        countries = scrape_pages(countries_with_urls())
        pickle.dump(countries, open(pickle_name, "wb"))
    countries = parse_countries(countries)
    export_countries_urls(countries)
    export_list_of_columns(countries)
    json.dump(countries, open("countries.json", "wt"), indent=0)
    pd.DataFrame.from_dict(countries, orient="index").to_csv("countries.csv", index_label="Country")

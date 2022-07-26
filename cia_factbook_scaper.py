import json
import logging
import os
import pickle

from bs4 import BeautifulSoup
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


def countries_with_urls():
    # {"name":"Italy","path":"/countries/italy/"},"ITA","IT | ITA | 380","ITA",".it",""
    lines_list = open("country_data_codes.csv", "rt").read().splitlines()[1:]
    # {"name":"Italy","path":"/countries/italy/
    lines_list = [txt.split("\"}", 1)[0] for txt in lines_list]
    countries = {}
    for line in lines_list:
        country_name = line.removeprefix("{\"name\":").split("\",", 1)[0]
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
            country["page_source"] = driver.page_source
        except Exception as e:
            logging.warning("Could not scrape the source from {}.\n{}".format("url", 2))
    driver.quit()


def parse_pages(countries):
    """Parse the page source for each country, then delete the page source"""

    for country in countries.values():
        page_source = country.pop("page_source")
        soup = BeautifulSoup(page_source, "html.parser")
        content = soup.find("div", class_="content-area-content")
        for section in content.children:
            h2_tag = section.find("h2")
            if h2_tag is None:
                continue
            section_name = h2_tag.text
            for h3 in section.find_all("h3"):
                column_name = ": ".join([section_name, h3.text])
                next_tag = h3.next_sibling
                if next_tag.text != "":
                    country[column_name] = next_tag.text
                else:
                    country[column_name] = next_tag.next_sibling.text


if __name__ == "__main__":
    pickle_name = "countries_with_page_source.pickle" 
    if not os.path.exists(pickle_name):
        countries_with_page_source = countries_with_urls()
        countries_with_page_source = scrape_pages(countries_with_page_source)
        pickle.dump(countries_with_page_source, open(pickle_name, "wb"))
    countries = pickle.load(open(pickle_name, "rb"))
    parse_pages(countries)
    json.dump(countries, open("countries.json", "wt"), indent=0)

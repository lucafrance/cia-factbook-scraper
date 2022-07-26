import json
import logging

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
            try: 
                section_name = section.find("h2").text
            except Exception as e:
                logging.warning("Found no h2 tag in at least one section.\n{}\n{}".format(e, section))
                continue
            for h3 in section.find_all("h3"):
                column_name = ": ".join([section_name, h3.text])
                country[column_name] = h3.next_sibling.text



if __name__ == "__main__":
    countries = {"Italy": {"url" : "https://www.cia.gov/the-world-factbook/countries/italy/"}}
    scrape_pages(countries)
    parse_pages(countries)
    json.dump(countries, open("countries.json", "wt"), indent=0)

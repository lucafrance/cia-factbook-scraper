from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


def scrape_pages(countries):
    """Scrape the page source from the CIA Factbook"""

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    for country_name in countries.keys():
        url = countries[country_name]["url"]
        driver.get(url)
        countries[country_name]["page_source"] = driver.page_source
    driver.quit()


def parse_pages(countries):
    """Parse the page source for each country, then delete the page source"""

    for country_name in countries.keys():
        # TODO parsing
        countries[country_name].pop("page_source")


if __name__ == "__main__":
    countries = {"Italy": {"url" : "https://www.cia.gov/the-world-factbook/countries/italy/"}}
    scrape_pages(countries)
    print(countries)
    parse_pages(countries)

# CIA - The World Factbook Scraper

**Note** The World Factbook has been discontinued without warning nor reasoning on February 4th, 2026 ([announcement](https://www.cia.gov/stories/story/spotlighting-the-world-factbook-as-we-bid-a-fond-farewell/), [associated press story](https://apnews.com/article/cia-world-factbook-ratcliffe-trump-fbec61ce16c4b3db59db9cefce0da043)). This dataset includes the data as of March 14th, 2025.

---

This is a scraper for [*The World Factbook*](https://www.cia.gov/the-world-factbook/).
The data is exported to a `json` and to a `csv`.

The exported data is in the public domain.
> The Factbook is in the public domain. Accordingly, it may be copied freely without permission of the Central Intelligence Agency (CIA). The official seal of the CIA, however, may NOT be copied without permission as required by the CIA Act of 1949 (50 U.S.C. section 403m). Misuse of the official seal of the CIA could result in civil and criminal penalties.
*[About The World Factbook - Copyright and Contributors](https://www.cia.gov/the-world-factbook/about/copyright-and-contributors/)*

The file `country_data_codes.csv` is used as the list of countries to scrape.
It is in the public domain, as it also provided by the CIA ([source](https://www.cia.gov/the-world-factbook/references/country-data-codes/)).

The resulting dataset is [available on kaggle](https://www.kaggle.com/datasets/lucafrance/the-world-factbook-by-cia).

## Possible improvements
- Remove text from numerical values and add text to column name.
    - Now: `column name = "Coastline"`, `value = "7,600 km"`
    - After: `column name = "Coastline (km)"`, `value = 7600`
- Scrape additional content:
    - when the page was last updated,
    - photos,
    - audio samples,
    - [oceans](https://www.cia.gov/the-world-factbook/oceans/atlantic-ocean/),
    - [references](https://www.cia.gov/the-world-factbook/references/),
    - the CIA world factbook from previous years.

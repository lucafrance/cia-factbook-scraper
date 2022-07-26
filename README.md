`country_data_codes.csv` downloaded from [here](https://www.cia.gov/the-world-factbook/references/country-data-codes/).

### Possible improvements
- Scrape the countries' photos.
- Scrape the CIA world factbook from previous years.
- Split lists in multiple columns, e.g. "Area" is currently just one column:
  - `total: 301,340 sq km`
  - `land: 294,140 sq km`
  - `water: 7,200 sq km`
  - `note: includes Sardinia and Sicily`
- Remove text from numerical values and add text to column name.
  - Now: `column name = "Coastline"`, `value = "7,600 km"`
  - After: `column name = "Coastline (sq km)"`, `value = 7600`

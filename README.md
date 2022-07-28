`country_data_codes.csv` downloaded from [here](https://www.cia.gov/the-world-factbook/references/country-data-codes/).

### Possible improvements
Export list of columns.

Scrape the countries' photos.

Scrape audio samples.

Scrape the CIA world factbook from previous years.

Remove text from numerical values and add text to column name.
- Now: `column name = "Coastline"`, `value = "7,600 km"`
- After: `column name = "Coastline (sq km)"`, `value = 7600`

Refractor code that handles `strong` tags.

Rename `next_tag` variable to something more meaningful.

Scrape when the page was last updated.

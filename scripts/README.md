# Scripts

## Developer environment

* Install Python ^3.8

    * [pyenv](https://github.com/pyenv/pyenv)
    * [pyenv-installer](https://github.com/pyenv/pyenv-installer)
    * [Common Build Problems](https://github.com/pyenv/pyenv/wiki/common-build-problems)

* Install [poetry](https://github.com/python-poetry/poetry) and project dependencies

```
python -m pip install poetry
poetry install
```

## Project overview

The `scrape` python module iterates over the list of businesses, skipping rows for which there is already an entry in the business database. New businesses must currently be added to the end of businesses_list.csv because deduplication is done by row index.

The script updates the business database CSV and generates geojson files indexed by business type for lazy filtering on the front-end.

Open issues:

- add another maps scraper for the businesses that we don't find in bing maps
- if scrapers don't work, fuzzy parse address from URL and reverse geocode to lat long
- scrape additional information such as cuisine type
- index "database" on multiple columns instead of the row index in the list of businesses
- CI/CD to run tests and generate geojson features

### Folder structure

* scrape/ -- python module to run the scraping process
* util/ -- helper module
    * feature_collection.py -- geojson helper file
    * maps_driver.py -- selenium web driver for bing maps
* data/ -- data folder
    * businesses_list.csv -- snapshot of [this list](https://docs.google.com/spreadsheets/d/1N38NS-e9TWDr8a2An7Q6TDAcIKx4HI2K_AahsbnW26M/) maintained by @yankeemagazine
    * businesses_db.csv -- parsed businesses with lat/long and contact information
* output/ -- generated geojson output

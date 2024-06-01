# Sofifa Scraper

Scrapes FIFA Player Ratings from https://sofifa.com/

> Note: Use responsibly. Do not overload sofifa.com server.

## Installing Requirements

Requires Python 3.6 or above.

Mac and Linux

    $ pip3 install -r requirements.txt

Windows

    $ pip install -r requirements.txt

## Execution

### CLI Arguments

* `-f` or `--filename` to pass output file name argument. Default value is `output.csv`.
* `--max_pages` to pass the maxmimum number of pages to scrape. Default value is `25`.
* `--year` or `-y` to pass the FIFA release year. Currently, data from year `2007` are available.

### Examples:

    $ python scrape_sofifa.py --max_pages 5 --filename data.csv

    $ python scrape_sofifa.py -f data.json

    $ python scrape_sofifa.py --filename data.json --year=2007

## Help

    $ python scrape_sofifa.py --help

    $ python scrape_sofifa.py -h

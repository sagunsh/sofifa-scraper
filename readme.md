# Sofifa Scraper

Scrapes FIFA20 Player Ratings from sofifa.com

## Installing Scrapy

Requires Python 3 and Scrapy 1.7

For Mac and Linux

    $ pip install Scrapy
    
For Windows user, in anaconda prompt

    $ conda install -c conda-forge scrapy

## Project and Spider

    $ scrapy startproject fifa20    # creates project
    $ cd fifa20
    $ scrapy genspider sofifa sofifa.com    # creates spider
    
## Executing

    $ scrapy crawl sofifa - fifa20_data.csv
    $ scrapy crawl sofifa - fifa20_data.json
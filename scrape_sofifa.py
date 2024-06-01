import argparse
import csv
import json
import re
import sys
from urllib.parse import urljoin
import random
import time

import requests
from parsel import Selector


def send_request(url, max_tries=10):
    headers = {'User-Agent': 'Mozilla'}
    tries = 0
    while tries < max_tries:
        try:
            r = requests.get(url, headers=headers, timeout=300)
            if r.ok:
                return r
        except Exception as e:
            print(e)

        tries += 1

    return None


def get_available_versions(selector):
    versions = {}
    for option in selector.css('select[name="version"]>option'):
        value = option.css('::attr(value)').get('').split('r=')[1].split('&')[0]
        version = option.css('::text').get()
        versions[version] = value
    return versions


def get_all_columns(selector):
    columns = {}
    for option in selector.css('select[name="showCol[]"] option'):
        value = option.css('::attr(value)').get()
        attribute = option.css('::text').get()
        columns[attribute] = value
    return columns


def build_url_with_columns(fifa_version, selected_columns, offset=0):
    url = f'https://sofifa.com/?r={fifa_version}&set=true'
    for attribute, value in selected_columns.items():
        url += f'&showCol[]={value}'

    url += f'&offset={offset}'
    return url


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sofifa.com scraper')
    parser.add_argument('-f', '--filename', default='output.csv', type=str,
                        help='output filename with extension (csv or json)')
    parser.add_argument('--max_pages', type=int, default=25,
                        help='maximum number of pages to scrape, if not provided then scrape all pages')
    parser.add_argument('-y', '--year', type=int, default=2023,
                        help='FIFA realease year (from 2007 to 2024)')
    args = parser.parse_args()

    # validate arguments
    if not args.filename.endswith(('.csv', '.json')):
        print(f'{args.filename} is not csv or json. Please provide a filename with .csv or .json extension')
        sys.exit()

    if args.year < 2007:
        print(f'year {args.year} is out of range. Please provide a year from 2007 to 2024')
        sys.exit()

    base_url = 'https://sofifa.com/'
    r = send_request(base_url)
    if not r:
        print(f'failed sending request to {base_url}')
        sys.exit()

    selector = Selector(text=r.text)

    versions = get_available_versions(selector)
    columns = get_all_columns(selector)

    year = str(args.year % 100).zfill(2)
    if args.year >= 2024:
        version_key = f'FC {year}'
    else:
        version_key = f'FIFA {year}'

    fifa_version = versions.get(version_key)
    if not fifa_version:
        print(f'can not find fifa version for year {args.year}')
        sys.exit()

    print(f'scraping data for {version_key}')

    scrape_url = build_url_with_columns(fifa_version, columns)

    all_players = []
    page = 1

    while True:
        print(f'scrape page {page}')
        r = send_request(scrape_url)
        if not r:
            print(f'failed scraping on page {page}')
            break

        selector = Selector(text=r.text)
        for player in selector.css('table>tbody>tr'):
            td_name = player.css('td')[1]

            player_data = {
                'name': td_name.css('a::attr(data-tippy-content)').get(),
                'url': urljoin('https://sofifa.com/', td_name.css('a::attr(href)').get()),
                'positions': ','.join(td_name.css('span.pos::text').extract()).strip(),
                'country': td_name.css('div img::attr(title)').get(),
                'image': player.css('td.a1 img::attr(data-src)').get(),
            }

            for column, value in columns.items():
                key = '_'.join(re.sub('[^0-9a-zA-Z\s]+', '', column).lower().strip().split())
                try:
                    value = int(''.join(player.css(f'td[data-col="{value}"] ::text').extract()).strip())
                except:
                    value = ''.join(player.css(f'td[data-col="{value}"] ::text').extract()).strip()
                    if value == '':
                        value = None

                player_data[key] = value

            all_players.append(player_data)

        page += 1
        if args.max_pages:
            if page > args.max_pages:
                print(f'maximum pages {args.max_pages} scraped')
                break

        next_page = None
        for pagination in selector.css('div.pagination>a'):
            text = pagination.css('::text').get('').strip()
            if text == 'Next':
                next_page = pagination.css('::attr(href)').get()

        if not next_page:
            print('no next page found')
            break

        # wait after each page
        time.sleep(random.uniform(1, 2))
        scrape_url = urljoin(base_url, next_page)

    print('saving data to files')
    if len(all_players) > 0:
        with open(args.filename, 'w') as fp:
            if args.filename.endswith('.csv'):
                writer = csv.DictWriter(fp, fieldnames=all_players[0].keys())
                writer.writeheader()
                writer.writerows(all_players)
            else:
                json.dump(all_players, fp, indent=2)

        print(f'saved {len(all_players)} records to {args.filename}')
    else:
        print('empty data')

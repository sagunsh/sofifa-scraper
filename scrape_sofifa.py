import argparse
import csv
import json
import re
import sys
from urllib.parse import urljoin

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


def build_url_with_columns(fifa_version, selected_columns):
    url = f'https://sofifa.com/?r={fifa_version}&set=true'
    for attribute, value in selected_columns.items():
        url += f'&showCol[]={value}'

    return url


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sofifa.com scraper')
    parser.add_argument('-f', '--filename', default='output.csv', type=str,
                        help='Output filename with extension (csv or json)')
    args = parser.parse_args()

    if not args.filename.endswith(('.csv', '.json')):
        print(f'{args.filename} is not csv or json... using default output.csv')
        output_filename = 'output.csv'
    else:
        output_filename = args.filename

    url = 'https://sofifa.com/'
    r = send_request(url)
    if not r:
        print(f'failed sending request to {url}')
        sys.exit()

    selector = Selector(text=r.text)

    versions = get_available_versions(selector)
    columns = get_all_columns(selector)

    fifa_version = versions['FIFA 23']
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
                'image': player.css('td.a1 img::attr(data-src)').get(),
                'name': td_name.css('a::attr(data-tippy-content)').get(),
                'url': urljoin('https://sofifa.com/', td_name.css('a::attr(href)').get()),
                'positions': ','.join(td_name.css('span.pos::text').extract()).strip(),
                'country': td_name.css('div img::attr(title)').get(),
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

        # next_page = selector.css('div.pagination>a::attr(href)').get()
        page += 1
        break

    if len(all_players) > 0:
        print('saving data to files')
        with open(output_filename, 'w') as fp:
            if output_filename.endswith('.csv'):
                writer = csv.DictWriter(fp, fieldnames=all_players[0].keys())
                writer.writeheader()
                writer.writerows(all_players)
            else:
                json.dump(all_players, fp, indent=2)

        print(f'saved {len(all_players)} records to {output_filename}')
    else:
        print('Empty data')
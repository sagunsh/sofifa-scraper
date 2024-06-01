import argparse
import csv
import json
import re
from urllib.parse import urljoin

import requests
from parsel import Selector

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

    headers = {'User-Agent': 'Mozilla'}

    url = 'https://sofifa.com/'
    r = requests.get(url, headers=headers)
    selector = Selector(text=r.text)

    versions = {}
    for option in selector.css('select[name="version"]>option'):
        value = option.css('::attr(value)').get('').split('r=')[1].split('&')[0]
        version = option.css('::text').get()
        versions[version] = value

    fifa_version = versions['FIFA 23']

    columns = {}
    for option in selector.css('select[name="showCol[]"] option'):
        value = option.css('::attr(value)').get()
        attribute = option.css('::text').get()
        columns[attribute] = value

    # building url
    scrape_url = f'https://sofifa.com/?r={fifa_version}&set=true'
    for attribute, value in columns.items():
        scrape_url += f'&showCol[]={value}'

    r = requests.get(scrape_url, headers=headers)
    selector = Selector(text=r.text)

    headers = []
    for header in selector.css('table>thead th'):
        headers.append(''.join(header.css(' ::text').extract()))

    all_players = []
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

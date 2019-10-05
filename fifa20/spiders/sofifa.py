# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class SofifaSpider(scrapy.Spider):
    name = 'sofifa'
    allowed_domains = ['sofifa.com']
    start_urls = ['https://sofifa.com/players?col=oa&sort=desc&showCol%5B%5D=pi&showCol%5B%5D=ae&showCol%5B%5D=hi&showCol%5B%5D=wi&showCol%5B%5D=pf&showCol%5B%5D=oa&showCol%5B%5D=pt&showCol%5B%5D=bo&showCol%5B%5D=bp&showCol%5B%5D=gu&showCol%5B%5D=jt&showCol%5B%5D=le&showCol%5B%5D=vl&showCol%5B%5D=wg&showCol%5B%5D=rc&showCol%5B%5D=ta&showCol%5B%5D=cr&showCol%5B%5D=fi&showCol%5B%5D=he&showCol%5B%5D=sh&showCol%5B%5D=vo&showCol%5B%5D=ts&showCol%5B%5D=dr&showCol%5B%5D=cu&showCol%5B%5D=fr&showCol%5B%5D=lo&showCol%5B%5D=bl&showCol%5B%5D=to&showCol%5B%5D=ac&showCol%5B%5D=sp&showCol%5B%5D=ag&showCol%5B%5D=re&showCol%5B%5D=ba&showCol%5B%5D=tp&showCol%5B%5D=so&showCol%5B%5D=ju&showCol%5B%5D=st&showCol%5B%5D=sr&showCol%5B%5D=ln&showCol%5B%5D=te&showCol%5B%5D=ar&showCol%5B%5D=in&showCol%5B%5D=po&showCol%5B%5D=vi&showCol%5B%5D=pe&showCol%5B%5D=cm&showCol%5B%5D=td&showCol%5B%5D=ma&showCol%5B%5D=sa&showCol%5B%5D=sl&showCol%5B%5D=tg&showCol%5B%5D=gd&showCol%5B%5D=gh&showCol%5B%5D=gk&showCol%5B%5D=gp&showCol%5B%5D=gr&showCol%5B%5D=tt&showCol%5B%5D=bs&showCol%5B%5D=wk&showCol%5B%5D=sk&showCol%5B%5D=aw&showCol%5B%5D=dw&showCol%5B%5D=ir&showCol%5B%5D=pac&showCol%5B%5D=sho&showCol%5B%5D=pas&showCol%5B%5D=dri&showCol%5B%5D=def&showCol%5B%5D=phy']

    def parse(self, response):
        headers = response.css('table.table>thead>tr>th ::text').extract()[5:]

        for player in response.css('table.table>tbody>tr'):
            item = {}
            item['Name'] = player.css('td.col-name>div>a::attr(title)').extract()[1]
            item['Image'] = player.css('figure.avatar>img::attr(data-src)').get()
            item['Country'] = player.css('td.col-name>div>a::attr(title)').extract()[0]
            item['Position'] = ','.join(player.css('td.col-name span.pos ::text').extract())
            item['Age'] = player.css('td.col-ae ::text').get()
            item['Overall'] = player.css('td.col-oa ::text').get()
            item['Potential'] = player.css('td.col-oa ::text').get()
            item['Club'] = player.css('td.col-name')[1].css('a ::text').get()

            value = list(map(str.strip, [p.css(' ::text').get() for p in player.css('td')[6:]]))
            item.update(dict(zip(headers, value)))
            yield item

        next_page = response.xpath('//span[@class="bp3-button-text" and text()="Next"]/parent::a/@href').get()
        if next_page:
            yield Request(response.urljoin(next_page))

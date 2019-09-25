# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class SofifaSpider(scrapy.Spider):
    name = 'sofifa'
    allowed_domains = ['sofifa.com']
    start_urls = ['https://sofifa.com/?col=oa&sort=desc&showCol%5B%5D=ae&showCol%5B%5D=hi&showCol%5B%5D=wi&showCol%5B%5D=pf&showCol%5B%5D=oa&showCol%5B%5D=pt&showCol%5B%5D=bo&showCol%5B%5D=bp&showCol%5B%5D=jt&showCol%5B%5D=vl&showCol%5B%5D=wg&showCol%5B%5D=rc&showCol%5B%5D=wk&showCol%5B%5D=sk&showCol%5B%5D=aw&showCol%5B%5D=dw&showCol%5B%5D=ir']

    def parse(self, response):
        for player in response.css('table.table>tbody>tr'):
            item = {}
            item['Country'] = player.css('td.col-name>div>a::attr(title)').extract()[0]
            item['Name'] = player.css('td.col-name>div>a::attr(title)').extract()[1]
            item['Club'] = player.css('td.col-name')[1].css('a ::text').get()
            item['Position'] = player.css('td.col-name span.pos ::text').get()
            item['Age'] = player.css('td.col-ae ::text').get()
            item['Overall'] = player.css('td.col-oa ::text').get()
            item['Potential'] = player.css('td.col-oa ::text').get()
            item['Height'] = player.css('td.col-hi ::text').get()
            item['PreferredFoot'] = player.css('td.col-pf ::text').get()
            item['BestOverall'] = player.css('td.col-bo ::text').get()
            item['BestPosition'] = player.css('td.col-bp ::text').get()
            item['Growth'] = player.css('td.col-gu ::text').get()
            item['Joined'] = player.css('td.col-jt ::text').get()
            item['Value'] = player.css('td.col-vl ::text').get()
            item['Wage'] = player.css('td.col-wg ::text').get()
            item['ReleaseClause'] = player.css('td.col-rc ::text').get()
            item['WeakFoot'] = player.css('td.col-wk ::text').get()
            item['SkillMoves'] = player.css('td.col-sk ::text').get()
            item['IntlReputation'] = player.css('td.col-ir ::text').get()
            item['AttackingWorkRate'] = player.css('td.col-aw ::text').get()
            item['DefensiveWorkRate'] = player.css('td.col-dw ::text').get()
            yield item

        next_page = response.xpath('//span[@class="bp3-button-text" and text()="Next"]/parent::a/@href').get()
        if next_page:
            yield Request(response.urljoin(next_page))

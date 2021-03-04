import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CmssItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CmssSpider(scrapy.Spider):
	name = 'cmss'
	start_urls = ['https://www.cmss.cz/novinky']

	def parse(self, response):
		articles = response.xpath('//div[@class="entry grid-col-1 entry-articles"]')
		for article in articles:
			date = article.xpath('.//span[@class="entry-meta-published"]//span[@class="entry-meta-value"]/text()').get()
			post_links = article.xpath('.//div[@class="entry-title"]/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//div[@class="pagination pagination__posts"]/ul/li[@class="next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1[@class="article-title"]/text()').get()
		content = response.xpath('//div[@class="col col-1-12 grid-12-12"]/div[@class="block block-inline"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CmssItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()

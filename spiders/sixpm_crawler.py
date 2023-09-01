from scrapy import Spider

from sixPmScraper.spiders.sixpm_parser import SixPmParser


class SixPmSpider(Spider):
    name = "6pm.com"
    product_parser = SixPmParser()
    start_urls = [
        "https://www.6pm.com",
    ]

    def parse(self, response, **kwargs):
        category_links = self.product_parser.product_categories_link(response)
        yield from response.follow_all(category_links, callback=self.process_products)

    def process_products(self, response):
        pagination_link = self.product_parser.product_page_pagination_link(response)
        products = self.product_parser.product_articles(response)
        yield from response.follow_all(products, callback=self.process_single_product,
                                       meta={'url_trail': response.url})
        if pagination_link:
            yield from response.follow(pagination_link, callback=self.process_products)

    def process_single_product(self, response):
        item = self.product_parser.parse_product(response)

        yield item

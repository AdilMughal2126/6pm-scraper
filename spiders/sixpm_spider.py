import copy

from scrapy import Spider

from sixPmScraper.constants import KEYWORDS_LIST
from sixPmScraper.items import ProductItem


class SixPMParseSpider(Spider):
    name = "6pm-parse"

    def parse(self, response):
        item = ProductItem()
        item['retailer_sku'] = self.product_retailer_sku(response)
        item['trail'] = self.product_url_trail(response)
        item['gender'] = self.product_gender(response)
        item['brand'] = self.product_brand(response)
        item['name'] = self.product_name(response)
        item['url'] = self.product_url(response)
        item['description'] = self.product_description(response)
        item['care'] = self.product_care(response)
        item['image_urls'] = self.product_image_urls(response)
        item['category'] = self.product_category(response)
        item['skus'] = self.product_skus(response)

        return item

    def product_image_urls(self, response):
        return [image.split(' ')[2] for image in response.css('#stage source::attr(srcset)').getall()]

    def product_url_trail(self, response):
        return response.meta.get('url_trail', [])

    def product_skus(self, response):
        skus = []

        stock_data = response.css('legend#sizingChooser+div input[type="radio"]::attr(data-label)').getall()
        size_data = response.css('legend#sizingChooser+div input[type="radio"]::attr(aria-label)').getall()

        for index, (stock, size) in enumerate(zip(stock_data, size_data)):
            sku = {}
            sku["price"] = self.product_price(response)
            sku["previous_price"] = self.product_previous_price(response)
            sku["currency"] = self.product_currency(response)
            sku["size"] = size
            sku["color"] = self.product_color(response)
            sku["out_of_stock"] = "Out" in stock
            sku["sku_id"] = self.product_sku_id(sku["color"], index)

            # Append the new SKU dictionary to the skus list
            skus.append(sku)

        return skus


    def product_sku_id(self, color, index):
        return f'{color.replace(" ", "")}_{index}'

    def product_color(self, response):
        return response.css('#buyBoxForm div span')[1].css('::text').get()

    def product_currency(self, response):
        return response.css('span[itemprop="priceCurrency"]::attr(content)').get()

    def product_previous_price(self, response):
        return response.css('span[itemprop="price"]+span span span+span::text').get()[1:]

    def product_price(self, response):
        return response.css('span[itemprop="price"]::attr(content)').get()

    def product_category(self, response):
        return response.css('#breadcrumbs a::text').getall()[1:]

    def product_description(self, response):
        return response.css('div[itemprop="description"] ul li::text').getall()

    def product_url(self, response):
        return response.url

    def product_name(self, response):
        return response.css('meta[itemprop="name"]::attr(content)').get()

    def product_brand(self, response):
        return response.css('span[itemprop="name"]::text').get()

    def product_retailer_sku(self, response):
        return response.css('span[itemprop="sku"]::text').get()

    def product_care(self, response):
        care = []

        for line in self.product_description(response):
            for keyword in KEYWORDS_LIST:
                if keyword.lower() in line.lower():
                    care.append(line)
                    break

        return care

    def product_gender(self, response):
        gender = response.css("#sizingChooser span::text").get().split(" ")[0]

        if gender.lower() not in ["women's", "men's"]:
            gender = "unisex-adults"

        return gender


class SixPMCrawlSpider(Spider):
    name = "6pm-crawl"
    start_urls = [
        "https://www.6pm.com",
    ]
    product_parser = SixPMParseSpider()

    def parse(self, response, **kwargs):
        trail = self.add_trail(response)
        selector = 'header[data-header-container="true"] div[data-sub-nav="true"] ul li a+div a::attr(href)'
        category_links = response.css(selector).getall()
        yield from response.follow_all(category_links, callback=self.parse_products,
                                       meta=trail.copy())

    def parse_products(self, response):
        trail = self.add_trail(response)
        pagination_link = response.css("#searchPagination a[rel='next']").get()
        products = response.css('#products article a')
        yield from response.follow_all(products, callback=lambda response: (yield self.product_parser.parse(response)),
                                       meta=trail.copy())

        yield from response.follow(pagination_link, callback=self.parse_products,
                                   meta={'url_trail': trail.copy()})

    def add_trail(self, response):
        url_trail = response.meta.get('url_trail', [])
        url_trail.append(response.url)
        return {'url_trail': url_trail}

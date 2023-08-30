import re
from pathlib import Path
from sixPmScraper.items import ProductItem
import scrapy


class ProductSpider(scrapy.Spider):
    name = "products"
    start_urls = [
        "https://www.6pm.com",
    ]

    def parse(self, response):
        # Doing this just to store the every
        # link that our spider follow from start to end product page
        url_trail = self.get_urltrail(response)

        category_links_siblings = response.xpath('//div[@class="Ci-z"]')
        category_links = category_links_siblings.xpath('preceding-sibling::a[1]')
        category_links = category_links[:-1]
        yield from response.follow_all(category_links, callback=self.parse_subcategory,
                                       meta={'url_trail': url_trail.copy()})

    def parse_subcategory(self, response):
        url_trail = self.get_urltrail(response)
        subcategories = response.css('div.Ms-z article a')

        for subcategory in subcategories:
            yield response.follow(subcategory, callback=self.parse_products,
                                  meta={'url_trail': url_trail.copy()})

    def parse_products(self, response):
        url_trail = self.get_urltrail(response)
        exclude_pattern = re.compile(r'^(?!.*product).*$', re.IGNORECASE)

        if exclude_pattern.match(response.url) and len(response.url) > 50:
            products = response.css('#products article a')
            yield from response.follow_all(products, callback=self.parse_single_product,
                                           meta={'url_trail': url_trail.copy()})

    def parse_single_product(self, response):
        url_trail = self.get_urltrail(response)
        product_images = response.css('#stage source::attr(srcset)').getall()
        product_images = [image.split(' ')[2] for image in product_images]

        sku_list = []
        for size in response.css('div.Mwa-z input[type="radio"]::attr(data-label)').getall():
            sku_dict = {
                "price": response.css('span[itemprop="price"]::attr(content)').get(),
                "previous_price": response.css('span.Kr-z::text').get(),
                "currency": response.css('span[itemprop="priceCurrency"]::attr(content)').get(),
                "size": size,
                "color": response.css('#buyBoxForm span.e2-z::text').get(),
            }
            sku_list.append(sku_dict)

        item = ProductItem()
        item['retailer_sku'] = response.css('span[itemprop="sku"]::text').get()
        item['trail'] = url_trail
        item['brand'] = response.css('span[itemprop="name"]::text').get()
        item['name'] = response.css('meta[itemprop="name"]::attr(content)').get()
        item['url'] = self.start_urls[0] + response.css('meta[itemprop="url"]::attr(content)').get()
        item['description'] = response.css('div[itemprop="description"] ul li::text').getall()
        item['product_images'] = product_images
        item['category'] = response.css('#breadcrumbs a::text').getall()[1]
        item['sku'] = sku_list

        yield item

    def get_urltrail(self, response):
        url_trail = response.meta.get('url_trail', [])
        url_trail.append(response.url)
        return url_trail

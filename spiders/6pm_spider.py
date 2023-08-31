from scrapy import Spider
from sixPmScraper.constants import KEYWORDS_LIST
from sixPmScraper.items import ProductItem


class SixPmSpider(Spider):
    name = "6pm.com"
    start_urls = [
        "https://www.6pm.com",
    ]

    def parse(self, response):
        category_links = response.css('div.xh-z a')
        yield from response.follow_all(category_links, callback=self.parse_products)

    def parse_products(self, response):
        pagination_link = response.css("#searchPagination a[rel='next']")
        products = response.css('#products article a')
        yield from response.follow_all(products, callback=self.parse_single_product,
                                       meta={'url_trail': response.url})
        if pagination_link:
            yield from response.follow(pagination_link, callback=self.parse_products)

    def parse_single_product(self, response):
        item = ProductItem()
        item['retailer_sku'] = self.extract_retailer_sku(response)
        item['trail'] = self.get_url_trail(response)
        item['gender'] = self.extract_gender(response)
        item['brand'] = self.extract_brand(response)
        item['name'] = self.extract_name(response)
        item['url'] = self.extract_url(response)
        item['description'] = self.extract_description(response)
        item['care'] = self.extract_care(response)
        item['image_urls'] = self.get_image_urls(response)
        item['category'] = self.extract_category(response)
        item['skus'] = self.extract_skuslist(response)

        yield item

    def get_image_urls(self, response):
        product_images = response.css('#stage source::attr(srcset)').getall()
        product_images = [image.split(' ')[2] for image in product_images]

        return product_images

    def get_url_trail(self, response):
        url_trail = response.meta.get('url_trail', []).split('/')
        root_url = f'{url_trail[2]}'
        main_category_url = f'{url_trail[2]}/{self.extract_category(response)}'
        products_url = response.meta.get('url_trail', [])

        return [root_url, main_category_url, products_url]

    def extract_skuslist(self, response):
        skus = []
        for size in response.css('div.Nva-z input[type="radio"]::attr(data-label)').getall():
            sku_dict = {
                "price": response.css('span[itemprop="price"]::attr(content)').get(),
                "previous_price": response.css('span.Kr-z::text').get(),
                "currency": response.css('span[itemprop="priceCurrency"]::attr(content)').get(),
                "size": size,
                "color": response.css('#buyBoxForm span.e2-z::text').get(),
            }
            skus.append(sku_dict)

        return skus

    def extract_category(self, response):
        return response.css('#breadcrumbs a::text').getall()[1:]

    def extract_description(self, response):
        return response.css('div[itemprop="description"] ul li::text').getall()

    def extract_url(self, response):
        return self.start_urls[0] + response.css('meta[itemprop="url"]::attr(content)').get()

    def extract_name(self, response):
        return response.css('meta[itemprop="name"]::attr(content)').get()

    def extract_brand(self, response):
        return response.css('span[itemprop="name"]::text').get()

    def extract_retailer_sku(self, response):
        return response.css('span[itemprop="sku"]::text').get()

    def extract_care(self, response):
        care = []

        for line in self.extract_description(response):
            for keyword in KEYWORDS_LIST:
                if keyword.lower() in line.lower():
                    care.append(line)
                    break

        return care

    def extract_gender(self, response):
        gender = response.css("#sizingChooser span::text").get().split(" ")[0]

        if gender.lower() not in ["women's", "men's"]:
            gender = "unisex-adults"

        return gender

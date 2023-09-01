from sixPmScraper.constants import KEYWORDS_LIST
from sixPmScraper.items import ProductItem


class SixPmParser:
    def parse_product(self, response):
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
        product_images = response.css('#stage source::attr(srcset)').getall()
        product_images = [image.split(' ')[2] for image in product_images]

        return product_images

    def product_url_trail(self, response):
        url_trail = response.meta.get('url_trail', []).split('/')
        root_url = url_trail[2]
        main_category_url = f'{url_trail[2]}/{self.product_category(response)[0]}'

        return [["", root_url], [self.product_category(response)[0], main_category_url]]

    def product_skus(self, response):
        skus, sku = [], {}
        for size in response.css('legend#sizingChooser+div input[type="radio"]::attr(data-label)').getall():
            sku["price"] = self.product_price(response)
            sku["previous_price"] = self.product_previous_price(response)
            sku["currency"] = self.product_currency(response)
            sku["size"] = size
            sku["color"] = self.product_color(response)
            skus.append(sku)

        return skus

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
        return response.css('meta[itemprop="url"]::attr(content)').get()

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

    def product_categories_link(self, response):
        selector = 'header[data-header-container="true"] div[data-sub-nav="true"] ul li a+div a::attr(href)'
        category_links = response.css(selector).getall()
        return category_links

    def product_articles(self, response):
        return response.css('#products article a')

    def product_page_pagination_link(self, response):
        pagination_link = response.css("#searchPagination a[rel='next']")
        return pagination_link

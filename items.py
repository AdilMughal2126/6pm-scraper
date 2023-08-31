from scrapy.item import Item, Field


class ProductItem(Item):
    retailer_sku = Field()
    trail = Field()
    gender = Field()
    brand = Field()
    url = Field()
    name = Field()
    description = Field()
    care = Field()
    image_urls = Field()
    category = Field()
    skus = Field()

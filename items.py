from scrapy.item import Item, Field


class ProductItem(Item):
    retailer_sku = Field()
    trail = Field()
    brand = Field()
    url = Field()
    name = Field()
    description = Field()
    product_images = Field()
    category = Field()
    sku = Field()

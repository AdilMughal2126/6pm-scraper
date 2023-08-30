from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


class ProductItem(Item):
    retailer_sku = Field(input_processors=MapCompose(remove_tags), output_processors=TakeFirst)
    trail = Field()
    brand = Field(input_processors=MapCompose(remove_tags), output_processors=TakeFirst)
    url = Field()
    name = Field(input_processors=MapCompose(remove_tags), output_processors=TakeFirst)
    description = Field()
    product_images = Field()
    category = Field()
    sku = Field()

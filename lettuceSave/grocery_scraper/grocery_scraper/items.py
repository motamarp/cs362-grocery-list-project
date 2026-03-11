import scrapy


class StoreIngredientItem(scrapy.Item):
    store_name = scrapy.Field()
    store_chain = scrapy.Field()
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()

    ingredient_name = scrapy.Field()
    price = scrapy.Field()
    price_unit = scrapy.Field()
    in_stock = scrapy.Field()
    brand = scrapy.Field()

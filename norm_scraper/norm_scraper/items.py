import scrapy


class NormScraperItem(scrapy.Item):
    article = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    current_retail = scrapy.Field()
    current_dealer = scrapy.Field()
    availability = scrapy.Field()
    photo = scrapy.Field()
    link = scrapy.Field()
    brand = scrapy.Field()
    pass

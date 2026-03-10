# Scrapy settings for grocery_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "grocery_scraper"

SPIDER_MODULES = ["grocery_scraper.spiders"]
NEWSPIDER_MODULE = "grocery_scraper.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 1

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

ITEM_PIPELINES = {
    "grocery_scraper.pipelines.GroceryScraperPipeline": 300,
}

LOG_LEVEL = "INFO"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

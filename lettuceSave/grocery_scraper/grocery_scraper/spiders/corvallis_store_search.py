import re
from pathlib import Path
import scrapy
from grocery_scraper.items import StoreIngredientItem


class CorvallisStoreSearchSpider(scrapy.Spider):
    name = "corvallis_store_search"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "LOG_LEVEL": "INFO",
    }

    STORE_INFO = {
        "walmart": {
            "store_name": "Walmart Neighborhood Market",
            "store_chain": "Walmart",
            "address": "1840 NW Ninth St, Corvallis, OR",
            "latitude": 44.5857,
            "longitude": -123.2794,
        },
        "fredmeyer": {
            "store_name": "Fred Meyer",
            "store_chain": "Fred Meyer",
            "address": "777 NW Kings Blvd, Corvallis, OR",
            "latitude": 44.5725,
            "longitude": -123.2750,
        },
        "safeway": {
            "store_name": "Safeway",
            "store_chain": "Safeway",
            "address": "450 SW Third St, Corvallis, OR",
            "latitude": 44.5601,
            "longitude": -123.2620,
        },
    }

    def __init__(self, queries="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queries = [q.strip().lower() for q in queries.split(",") if q.strip()]
        self.debug_dir = Path(__file__).resolve().parents[2] / "debug_output"
        self.debug_dir.mkdir(exist_ok=True)

    def start_requests(self):
        if not self.queries:
            self.logger.warning("No queries passed. Example: -a queries=milk,bread")
            return

        for query in self.queries:
            walmart_url = f"https://www.walmart.com/search?q={query}"
            fredmeyer_url = f"https://www.fredmeyer.com/search?query={query}"
            safeway_url = f"https://www.safeway.com/shop/search-results.html?q={query}"

            yield scrapy.Request(
                walmart_url,
                callback=self.parse_walmart,
                cb_kwargs={"query": query},
                dont_filter=True,
            )
            yield scrapy.Request(
                fredmeyer_url,
                callback=self.parse_fredmeyer,
                cb_kwargs={"query": query},
                dont_filter=True,
            )
            yield scrapy.Request(
                safeway_url,
                callback=self.parse_safeway,
                cb_kwargs={"query": query},
                dont_filter=True,
            )

    def save_debug_html(self, filename, response):
        path = self.debug_dir / filename
        path.write_text(response.text, encoding="utf-8")
        self.logger.info(f"Saved debug HTML: {path}")

    def parse_walmart(self, response, query):
        self.logger.info(f"Walmart status={response.status} url={response.url}")
        self.save_debug_html(f"walmart_{query}.html", response)

        store = self.STORE_INFO["walmart"]

        selectors_to_try = [
            "div[data-item-id]",
            "[data-automation-id='product-title']",
            "div.mb0",
        ]

        for sel in selectors_to_try:
            count = len(response.css(sel))
            self.logger.info(f"Walmart selector '{sel}' found {count} matches")

        product_cards = response.css("div[data-item-id]")
        if not product_cards:
            self.logger.info(f"Walmart: no product cards found for {query}")
            return

        found_any = False

        for card in product_cards[:10]:
            title = (
                card.css("span[data-automation-id='product-title']::text").get()
                or "".join(card.css("span::text").getall()).strip()
            )

            price_text = (
                card.css("[itemprop='price']::attr(content)").get()
                or "".join(card.css("span::text").getall())
            )

            self.logger.info(f"Walmart raw title={title!r} raw price={price_text!r}")

            if not title or not price_text:
                continue

            price = self.extract_price(price_text)
            if price is None:
                continue

            found_any = True

            yield StoreIngredientItem(
                store_name=store["store_name"],
                store_chain=store["store_chain"],
                address=store["address"],
                latitude=store["latitude"],
                longitude=store["longitude"],
                ingredient_name=query,
                price=price,
                price_unit="each",
                in_stock=True,
                brand=self.extract_brand(title),
            )

        if not found_any:
            self.logger.info(f"Walmart parsed cards but yielded no items for {query}")

    def parse_fredmeyer(self, response, query):
        self.logger.info(f"Fred Meyer status={response.status} url={response.url}")
        self.save_debug_html(f"fredmeyer_{query}.html", response)

        store = self.STORE_INFO["fredmeyer"]

        selectors_to_try = [
            "div[data-testid='auto-grid-cell']",
            "div.kds-Card",
            "[data-testid='product-description']",
        ]

        for sel in selectors_to_try:
            count = len(response.css(sel))
            self.logger.info(f"Fred Meyer selector '{sel}' found {count} matches")

        product_cards = response.css("div[data-testid='auto-grid-cell'], div.kds-Card")
        if not product_cards:
            self.logger.info(f"Fred Meyer: no product cards found for {query}")
            return

        found_any = False

        for card in product_cards[:10]:
            title = (
                card.css("h3::text").get()
                or card.css("[data-testid='product-description']::text").get()
                or "".join(card.css("a::text").getall()).strip()
            )

            price_text = "".join(card.css("span::text").getall())

            self.logger.info(f"Fred Meyer raw title={title!r} raw price={price_text!r}")

            if not title or not price_text:
                continue

            price = self.extract_price(price_text)
            if price is None:
                continue

            found_any = True

            yield StoreIngredientItem(
                store_name=store["store_name"],
                store_chain=store["store_chain"],
                address=store["address"],
                latitude=store["latitude"],
                longitude=store["longitude"],
                ingredient_name=query,
                price=price,
                price_unit="each",
                in_stock=True,
                brand=self.extract_brand(title),
            )

        if not found_any:
            self.logger.info(f"Fred Meyer parsed cards but yielded no items for {query}")

    def parse_safeway(self, response, query):
        self.logger.info(f"Safeway status={response.status} url={response.url}")
        self.save_debug_html(f"safeway_{query}.html", response)

        store = self.STORE_INFO["safeway"]

        selectors_to_try = [
            "div.product-tile",
            "div[data-test='product-card']",
            ".product-title",
        ]

        for sel in selectors_to_try:
            count = len(response.css(sel))
            self.logger.info(f"Safeway selector '{sel}' found {count} matches")

        product_cards = response.css("div.product-tile, div[data-test='product-card']")
        if not product_cards:
            self.logger.info(f"Safeway: no product cards found for {query}")
            return

        found_any = False

        for card in product_cards[:10]:
            title = (
                card.css(".product-title::text").get()
                or "".join(card.css("a::text").getall()).strip()
            )

            price_text = "".join(card.css("span::text").getall())

            self.logger.info(f"Safeway raw title={title!r} raw price={price_text!r}")

            if not title or not price_text:
                continue

            price = self.extract_price(price_text)
            if price is None:
                continue

            found_any = True

            yield StoreIngredientItem(
                store_name=store["store_name"],
                store_chain=store["store_chain"],
                address=store["address"],
                latitude=store["latitude"],
                longitude=store["longitude"],
                ingredient_name=query,
                price=price,
                price_unit="each",
                in_stock=True,
                brand=self.extract_brand(title),
            )

        if not found_any:
            self.logger.info(f"Safeway parsed cards but yielded no items for {query}")

    def extract_price(self, text):
        match = re.search(r"(\d+\.\d{2})", text)
        if match:
            return match.group(1)
        return None

    def extract_brand(self, title):
        words = title.split()
        return words[0] if words else ""

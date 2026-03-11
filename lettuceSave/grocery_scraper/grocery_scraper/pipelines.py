import os
import sys
from pathlib import Path

# Point Scrapy to the Django project
BASE_DIR = Path(__file__).resolve().parents[2]  # .../lettuceSave
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lettucesave_project.settings")

import django
django.setup()

from planner.models import Store, StoreIngredient


class GroceryScraperPipeline:
    def process_item(self, item, spider):
        store, _ = Store.objects.get_or_create(
            name=item["store_name"],
            defaults={
                "chain": item.get("store_chain", ""),
                "address": item.get("address", ""),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
            },
        )

        # Update store info if it already exists
        store.chain = item.get("store_chain", store.chain)
        store.address = item.get("address", store.address)
        store.latitude = item.get("latitude", store.latitude)
        store.longitude = item.get("longitude", store.longitude)
        store.save()

        StoreIngredient.objects.update_or_create(
            store=store,
            ingredient_name=item["ingredient_name"].strip().lower(),
            brand=item.get("brand", "").strip(),
            defaults={
                "price": item["price"],
                "price_unit": item.get("price_unit", "each"),
                "in_stock": item.get("in_stock", True),
            },
        )

        return item

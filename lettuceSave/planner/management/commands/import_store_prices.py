import csv
from django.core.management.base import BaseCommand
from planner.models import Store, StoreIngredient

STORE_MAP = {
    "walmart": {
        "name": "Walmart Neighborhood Market",
        "address": "1840 NW Ninth St, Corvallis, OR",
        "chain": "Walmart"
    },
    "fred_meyer": {
        "name": "Fred Meyer",
        "address": "777 NW Kings Blvd, Corvallis, OR",
        "chain": "Fred Meyer"
    },
    "safeway": {
        "name": "Safeway",
        "address": "450 SW Third St, Corvallis, OR",
        "chain": "Safeway"
    }
}

class Command(BaseCommand):
    help = "Import grocery prices from CSV"

    def handle(self, *args, **kwargs):
        path = "planner/data/store_prices.csv"

        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                store_info = STORE_MAP[row["store_key"]]

                store, _ = Store.objects.get_or_create(
                    name=store_info["name"],
                    defaults={
                        "address": store_info["address"],
                        "chain": store_info["chain"]
                    }
                )

                StoreIngredient.objects.update_or_create(
                    store=store,
                    ingredient_name=row["ingredient_name"],
                    brand=row["brand"],
                    defaults={
                        "price": row["price"],
                        "price_unit": row["price_unit"],
                        "in_stock": row["in_stock"].lower() == "true"
                    }
                )

        self.stdout.write(self.style.SUCCESS("Imported grocery dataset successfully."))

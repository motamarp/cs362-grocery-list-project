from django.core.management.base import BaseCommand
from planner.models import Store, StoreIngredient


class Command(BaseCommand):
    help = "Seed Corvallis grocery stores and sample inventory"

    def handle(self, *args, **kwargs):
        # Clear old sample inventory
        StoreIngredient.objects.all().delete()
        Store.objects.all().delete()

        walmart = Store.objects.create(
            name="Walmart Neighborhood Market",
            chain="Walmart",
            address="1840 NW Ninth St, Corvallis, OR",
            latitude=44.5857,
            longitude=-123.2794
        )

        fred_meyer = Store.objects.create(
            name="Fred Meyer",
            chain="Fred Meyer",
            address="777 NW Kings Blvd, Corvallis, OR",
            latitude=44.5725,
            longitude=-123.2750
        )

        safeway = Store.objects.create(
            name="Safeway",
            chain="Safeway",
            address="450 SW Third St, Corvallis, OR",
            latitude=44.5601,
            longitude=-123.2620
        )

        sample_items = [
            # Walmart
            (walmart, "milk", 3.49, "gallon", True, "Great Value"),
            (walmart, "eggs", 2.99, "dozen", True, "Great Value"),
            (walmart, "bread", 2.48, "loaf", True, "Wonder"),
            (walmart, "bananas", 0.58, "lb", True, "Fresh"),
            (walmart, "rice", 4.98, "5 lb bag", True, "Great Value"),
            (walmart, "chicken breast", 3.99, "lb", True, "Tyson"),

            # Fred Meyer
            (fred_meyer, "milk", 3.79, "gallon", True, "Kroger"),
            (fred_meyer, "eggs", 3.29, "dozen", True, "Kroger"),
            (fred_meyer, "bread", 2.99, "loaf", True, "Oroweat"),
            (fred_meyer, "bananas", 0.69, "lb", True, "Fresh"),
            (fred_meyer, "rice", 5.49, "5 lb bag", True, "Kroger"),
            (fred_meyer, "chicken breast", 4.49, "lb", True, "Simple Truth"),

            # Safeway
            (safeway, "milk", 4.19, "gallon", True, "Lucerne"),
            (safeway, "eggs", 3.49, "dozen", True, "Lucerne"),
            (safeway, "bread", 3.29, "loaf", True, "Oroweat"),
            (safeway, "bananas", 0.79, "lb", True, "Fresh"),
            (safeway, "rice", 5.99, "5 lb bag", True, "Signature Select"),
            (safeway, "chicken breast", 4.99, "lb", True, "Signature Farms"),
        ]

        for store, ingredient_name, price, price_unit, in_stock, brand in sample_items:
            StoreIngredient.objects.create(
                store=store,
                ingredient_name=ingredient_name,
                price=price,
                price_unit=price_unit,
                in_stock=in_stock,
                brand=brand
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded store data."))

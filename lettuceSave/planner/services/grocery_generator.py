from collections import defaultdict
from planner.models import GroceryList, GroceryListItem, StoreIngredient

def generate_grocery_list(meal_plan):
    """
    Generate a grocery list from a meal plan.
    Aggregates ingredients from all planned meals, finds best prices, and creates a GroceryList.
    Returns the created GroceryList instance.
    """
    # Aggregate ingredients
    ingredient_dict = defaultdict(lambda: {'quantity': 0.0, 'metric': None, 'recipes': []})

    for planned_meal in meal_plan.meals.all():
        if not planned_meal.recipe:
            continue
        for ingredient in planned_meal.recipe.ingredients.all():
            key = ingredient.name
            ingredient_dict[key]['quantity'] += ingredient.quantity
            ingredient_dict[key]['metric'] = ingredient.metric
            ingredient_dict[key]['recipes'].append(planned_meal.recipe)

    if not ingredient_dict:
        return None

    # Get user's favorite stores to prioritize
    favorite_stores = []
    if hasattr(meal_plan.user, 'profile') and meal_plan.user.profile.favorite_stores:
        favorite_stores = [s.strip() for s in meal_plan.user.profile.favorite_stores.split(',') if s.strip()]

    # Create grocery list
    grocery_list = GroceryList.objects.create(
        meal_plan=meal_plan,
        name=f"Grocery list for week of {meal_plan.week_start_date}"
    )

    # For each ingredient, find best price (prioritize favorite stores if desired)
    for name, data in ingredient_dict.items():
        # Get all in-stock store ingredients matching the name
        store_ingredients = StoreIngredient.objects.filter(
            ingredient_name__icontains=name,
            in_stock=True
        ).select_related('store').order_by('price')

        #  Prioritize favorite stores
        if favorite_stores:
            # Sort by whether store is in favorites, then by price
            store_ingredients = sorted(store_ingredients, key=lambda si: (si.store.name not in favorite_stores, si.price))
            # If  want cheapest among favorites,  first filter favorites
            fav_items = [si for si in store_ingredients if si.store.name in favorite_stores]
            if fav_items:
                best = fav_items[0]  # cheapest among favorites (since sorted by price)
            else:
                best = store_ingredients[0] if store_ingredients else None
        else:
            best = store_ingredients.first()

        price_estimate = best.price if best else None
        suggested_store = best.store if best else None

        # Create the item
        item = GroceryListItem.objects.create(
            grocery_list=grocery_list,
            ingredient_name=name,
            quantity=data['quantity'],
            metric=data['metric'],
            suggested_store=suggested_store,
            price_estimate=price_estimate
        )
        # Update totals
        item.source_recipes.set(data['recipes'])

    # Update totals
    grocery_list.recalculate_total()
    return grocery_list
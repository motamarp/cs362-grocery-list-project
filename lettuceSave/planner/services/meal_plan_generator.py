import random
from datetime import timedelta
from planner.models import Recipe, MealPlan, PlannedMeal

def generate_meal_plan(user, week_start_date, dietary_preferences=None):
    """
    Generate a meal plan for a user for the week starting on week_start_date.
    Returns the created MealPlan instance.
    """
    # If dietary_preferences not provided, get from user's profile
    if dietary_preferences is None and hasattr(user, 'profile'):
        profile = user.profile
        if profile.dietary_preferences:
            # Convert comma-separated string to list
            dietary_preferences = [p.strip() for p in profile.dietary_preferences.split(',') if p.strip()]
        else:
            dietary_preferences = []

    # Use activity level to influence recipe selection (e.g., prefer higher-calorie meals for active users)
    activity_level = getattr(user.profile, 'activity_level', 3) if hasattr(user, 'profile') else 3
    # For now, we just log it, but you could adjust calorie targets later.

    # Base queryset: all recipes
    recipes = Recipe.objects.all()

    # Filter by dietary preferences if any
    if dietary_preferences:
        # This is simplistic: we filter recipes whose dietary_tags (a JSON list) contains any of the preferences.
        # More robust would be to use Django's JSONField lookups, but for simplicity we'll use Python filtering.
        # Since dietary_tags is a JSON list, we can use __contains lookup for exact match? Actually, __contains works on JSONField for keys/values, but for array containment we can use __overlap if using Postgres.
        # For SQLite, we may need to do in-memory filtering. Let's keep it simple: filter recipes where any of the dietary_preferences is in the dietary_tags list.
        # We'll do it in Python after fetching. For large datasets, this is inefficient, but for now it's okay.
        all_recipes = list(recipes)
        filtered = []
        for recipe in all_recipes:
            tags = recipe.dietary_tags
            if any(pref in tags for pref in dietary_preferences):
                filtered.append(recipe)
        recipes = filtered
    else:
        recipes = list(recipes)

    # Define meal types for each day (breakfast, lunch, dinner)
    meal_types = ['breakfast', 'lunch', 'dinner']

    # Create a new meal plan
    meal_plan = MealPlan.objects.create(
        user=user,
        week_start_date=week_start_date,
        is_active=True
    )

    # For each day of the week (0=Monday to 6=Sunday)
    for day in range(7):
        for meal_type in meal_types:
            # Filter recipes by meal_type (optional)
            candidates = [r for r in recipes if r.meal_type == meal_type]
            if not candidates:
                candidates = recipes  # fallback to any recipe

            if candidates:
                recipe = random.choice(candidates)
            else:
                recipe = None

            # Create planned meal
            PlannedMeal.objects.create(
                meal_plan=meal_plan,
                day_of_week=day,
                meal_type=meal_type,
                recipe=recipe
            )

    return meal_plan
from rest_framework import serializers
from .models import (
    Recipe, RecipeIngredient, Store, StoreIngredient,
    MealPlan, PlannedMeal, GroceryList, GroceryListItem
)


def format_nutrition_display(nutrition_data):
    if isinstance(nutrition_data, dict):
        return nutrition_data
    elif isinstance(nutrition_data, list):
        labels = ['calories', 'protein', 'carbs', 'fat', 'fiber']
        return {labels[i]: val for i, val in enumerate(nutrition_data) if i < len(labels)}
    return {}


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'quantity', 'metric', 'category']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    total_time = serializers.IntegerField(source='total_time_minutes', read_only=True)
    nutrition_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'meal_type',
            'prep_time_minutes', 'cook_time_minutes', 'total_time',
            'difficulty', 'nutrition', 'nutrition_info',
            'dietary_tags', 'estimated_cost', 'instructions', 'ingredients'
        ]

    def get_nutrition_info(self, obj):
        return format_nutrition_display(obj.nutrition)


class RecipeBasicSerializer(serializers.ModelSerializer):
    calories = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'meal_type', 'calories', 'estimated_cost']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'chain', 'latitude', 'longitude']


class StoreIngredientSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_address = serializers.CharField(source='store.address', read_only=True)
    store_chain = serializers.CharField(source='store.chain', read_only=True)
    store_latitude = serializers.FloatField(source='store.latitude', read_only=True)
    store_longitude = serializers.FloatField(source='store.longitude', read_only=True)

    class Meta:
        model = StoreIngredient
        fields = [
            'id',
            'store',
            'store_name',
            'store_address',
            'store_chain',
            'store_latitude',
            'store_longitude',
            'ingredient_name',
            'price',
            'price_unit',
            'in_stock',
            'brand',
            'last_updated'
        ]


class GroceryListItemSerializer(serializers.ModelSerializer):
    suggested_store_name = serializers.CharField(source='suggested_store.name', read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = GroceryListItem
        fields = [
            'id',
            'grocery_list',
            'ingredient_name',
            'quantity',
            'metric',
            'suggested_store',
            'suggested_store_name',
            'price_estimate',
            'brand',
            'total_price',
            'is_purchased'
        ]


class GroceryListSerializer(serializers.ModelSerializer):
    items = GroceryListItemSerializer(many=True, read_only=True)
    meal_plan_week = serializers.DateField(source='meal_plan.week_start_date', read_only=True)
    items_by_store = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroceryList
        fields = ['id', 'name', 'meal_plan', 'created_at', 'total_cost', 'items', 'meal_plan_week', 'items_by_store']
        extra_kwargs = {
            'meal_plan': {'required': True}
        }

    def get_items_by_store(self, obj):
        grouped = {}
        for item in obj.items.all():
            store_name = item.suggested_store.name if item.suggested_store else "No store"
            if store_name not in grouped:
                grouped[store_name] = []
            grouped[store_name].append(GroceryListItemSerializer(item).data)
        return grouped



class PlannedMealSerializer(serializers.ModelSerializer):
    recipe_details = RecipeBasicSerializer(source='recipe', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = PlannedMeal
        fields = [
            'id', 'meal_plan', 'day_of_week', 'day_name', 'meal_type',
            'recipe', 'recipe_details', 'custom_notes', 'was_completed'
        ]


class MealPlanSerializer(serializers.ModelSerializer):
    meals = PlannedMealSerializer(many=True, read_only=True)
    week_end_date = serializers.DateField(read_only=True)
    grocery_list = GroceryListSerializer(read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MealPlan
        fields = [
            'id', 'user', 'user_name', 'week_start_date', 'week_end_date',
            'total_cost_estimate', 'is_active', 'meals', 'grocery_list'
        ]
        read_only_fields = ['user']

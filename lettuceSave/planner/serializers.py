from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Recipe, RecipeIngredient, Store, StoreIngredient,
    MealPlan, PlannedMeal, GroceryList, GroceryListItem
)

# ========== HELPER FUNCTIONS ==========

def format_nutrition_display(nutrition_data):
    """Helper function to format nutrition data for display"""
    if isinstance(nutrition_data, dict):
        return nutrition_data
    elif isinstance(nutrition_data, list):
        # Convert list to dict with standard labels
        labels = ['calories', 'protein', 'carbs', 'fat', 'fiber']
        return {labels[i]: val for i, val in enumerate(nutrition_data) if i < len(labels)}
    return {}

# ========== RECIPE SERIALIZERS ==========

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Basic serializer for recipe ingredients"""
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'quantity', 'metric', 'category']


class RecipeSerializer(serializers.ModelSerializer):
    """
    Main recipe serializer.
    Handles both input/output with nutrition as list for easy API use.
    """
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    total_time = serializers.IntegerField(source='total_time_minutes', read_only=True)
    
    # Accept nutrition as a list for easier input
    nutrition_list = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True,
        required=False,
        help_text="Input as [calories, protein, carbs, fat, fiber]"
    )
    
    # Display nutrition as formatted dict
    nutrition_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'meal_type', 
            'prep_time_minutes', 'cook_time_minutes', 'total_time',
            'difficulty', 'nutrition', 'nutrition_list', 'nutrition_info',
            'dietary_tags', 'estimated_cost', 'instructions', 'ingredients'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_nutrition_info(self, obj):
        """Format nutrition for display"""
        return format_nutrition_display(obj.nutrition)

    def create(self, validated_data):
        # Handle nutrition list if provided
        nutrition_list = validated_data.pop('nutrition_list', [])
        if nutrition_list:
            validated_data['nutrition'] = nutrition_list
        return super().create(validated_data)

    def update(self, instance, validated_data):
        nutrition_list = validated_data.pop('nutrition_list', None)
        if nutrition_list is not None:
            validated_data['nutrition'] = nutrition_list
        return super().update(instance, validated_data)


class RecipeBasicSerializer(serializers.ModelSerializer):
    """Minimal recipe info for dropdowns and summaries"""
    calories = serializers.IntegerField( read_only=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'meal_type', 'calories', 'estimated_cost']


# ========== STORE SERIALIZERS ==========

class StoreIngredientSerializer(serializers.ModelSerializer):
    """Serializer for store inventory items"""
    store_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = StoreIngredient
        fields = ['id', 'ingredient_name', 'price', 'price_unit', 'in_stock', 'brand', 'store_name']


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for stores with their inventory"""
    inventory = StoreIngredientSerializer(many=True, read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'chain', 'inventory']


# ========== GROCERY LIST SERIALIZERS ==========

class GroceryListItemSerializer(serializers.ModelSerializer):
    """Serializer for individual grocery items"""
    suggested_store_name = serializers.CharField(source='suggested_store.name', read_only=True)
    recipe_sources = serializers.StringRelatedField(many=True, source='source_recipes', read_only=True)
    
    class Meta:
        model = GroceryListItem
        fields = [
            'id', 'ingredient_name', 'quantity', 'metric',
            'suggested_store', 'suggested_store_name', 'price_estimate',
            'is_purchased', 'recipe_sources'
        ]


class GroceryListSerializer(serializers.ModelSerializer):
    """Serializer for grocery lists with their items"""
    items = GroceryListItemSerializer(many=True, read_only=True)
    meal_plan_week = serializers.DateField(source='meal_plan.week_start_date', read_only=True)
    
    class Meta:
        model = GroceryList
        fields = ['id', 'name', 'meal_plan', 'created_at', 'total_cost', 'items', 'meal_plan_week']


# ========== MEAL PLAN SERIALIZERS ==========

class PlannedMealSerializer(serializers.ModelSerializer):
    """Serializer for individual planned meals"""
    recipe_details = RecipeBasicSerializer(source='recipe', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = PlannedMeal
        fields = [
            'id', 'meal_plan', 'day_of_week', 'day_name', 'meal_type',
            'recipe', 'recipe_details', 'custom_notes', 'was_completed'
        ]


class MealPlanSerializer(serializers.ModelSerializer):
    """
    Main meal plan serializer.
    Shows all meals and the generated grocery list.
    """
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


class CreateMealPlanSerializer(serializers.Serializer):
    """
    Serializer for creating a new meal plan.
    Accepts optional preferences for generation.
    """
    week_start_date = serializers.DateField(required=False, help_text="Must be a Monday")
    dietary_preferences = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="e.g., ['vegetarian', 'gluten-free']"
    )
    
    def validate_week_start_date(self, value):
        """Ensure date is a Monday if provided"""
        if value and value.weekday() != 0:  # 0 = Monday
            raise serializers.ValidationError("Week must start on a Monday")
        return value


class SwapMealSerializer(serializers.Serializer):
    """
    Serializer for swapping a meal in an existing plan.
    """
    day_of_week = serializers.ChoiceField(choices=[0, 1, 2, 3, 4, 5, 6])
    meal_type = serializers.ChoiceField(choices=['breakfast', 'lunch', 'dinner', 'snack'])
    new_recipe_id = serializers.IntegerField(min_value=1)

    def validate_new_recipe_id(self, value):
        """Verify recipe exists"""
        if not Recipe.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipe not found")
        return value
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Recipe, RecipeIngredient, Store, StoreIngredient,
    MealPlan, PlannedMeal, GroceryList, GroceryListItem
)


# ========== RECIPE SERIALIZERS ==========

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for recipe ingredients"""
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'quantity', 'metric', 'category']


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Detailed recipe serializer with ingredients"""
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    total_time = serializers.IntegerField(source='total_time_minutes', read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'meal_type', 'prep_time_minutes',
            'cook_time_minutes', 'total_time', 'difficulty', 'nutrition',
            'dietary_tags', 'estimated_cost', 'instructions', 'ingredients',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RecipeBasicSerializer(serializers.ModelSerializer):
    """Minimal recipe info for meal plan display"""
    calories = serializers.IntegerField(source='calories', read_only=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'meal_type', 'calories', 'estimated_cost', 'difficulty']


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating recipes with nested ingredients"""
    ingredients = RecipeIngredientSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = [
            'name', 'description', 'meal_type', 'prep_time_minutes',
            'cook_time_minutes', 'difficulty', 'nutrition',
            'dietary_tags', 'estimated_cost', 'instructions', 'ingredients'
        ]
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        
        return recipe
    
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        
        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ingredients if provided
        if ingredients_data is not None:
            # Remove old ingredients
            instance.ingredients.all().delete()
            # Create new ones
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        
        return instance


# ========== STORE SERIALIZERS ==========

class StoreIngredientSerializer(serializers.ModelSerializer):
    """Serializer for store inventory items"""
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = StoreIngredient
        fields = [
            'id', 'store', 'store_name', 'ingredient_name',
            'price', 'price_unit', 'in_stock', 'brand', 'last_updated'
        ]
        read_only_fields = ['last_updated']


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for stores with optional inventory"""
    inventory = StoreIngredientSerializer(many=True, read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'chain', 'inventory']


# ========== GROCERY LIST SERIALIZERS ==========

class GroceryListItemSerializer(serializers.ModelSerializer):
    """Serializer for individual grocery list items"""
    suggested_store_name = serializers.CharField(
        source='suggested_store.name', 
        read_only=True
    )
    source_recipe_names = serializers.SerializerMethodField()
    
    class Meta:
        model = GroceryListItem
        fields = [
            'id', 'ingredient_name', 'quantity', 'metric',
            'suggested_store', 'suggested_store_name', 'price_estimate',
            'is_purchased', 'source_recipes', 'source_recipe_names'
        ]
    
    def get_source_recipe_names(self, obj):
        """Get names of recipes this item comes from"""
        return [recipe.name for recipe in obj.source_recipes.all()]


class GroceryListDetailSerializer(serializers.ModelSerializer):
    """Detailed grocery list with items"""
    items = GroceryListItemSerializer(many=True, read_only=True)
    meal_plan_id = serializers.IntegerField(source='meal_plan.id', read_only=True)
    meal_plan_week = serializers.DateField(source='meal_plan.week_start_date', read_only=True)
    
    class Meta:
        model = GroceryList
        fields = [
            'id', 'name', 'meal_plan', 'meal_plan_id', 'meal_plan_week',
            'created_at', 'updated_at', 'total_cost', 'items'
        ]
        read_only_fields = ['created_at', 'updated_at']


class GroceryListBasicSerializer(serializers.ModelSerializer):
    """Simple grocery list serializer for lists"""
    class Meta:
        model = GroceryList
        fields = ['id', 'name', 'created_at', 'total_cost']


# ========== MEAL PLAN SERIALIZERS ==========

class PlannedMealSerializer(serializers.ModelSerializer):
    """Serializer for individual planned meals"""
    recipe_details = RecipeBasicSerializer(source='recipe', read_only=True)
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PlannedMeal
        fields = [
            'id', 'day_of_week', 'day_name', 'meal_type',
            'recipe', 'recipe_details', 'custom_notes', 'was_completed'
        ]
    
    def get_day_name(self, obj):
        """Convert day number to name"""
        return obj.get_day_of_week_display()


class MealPlanSerializer(serializers.ModelSerializer):
    """Full meal plan serializer with all meals"""
    meals = PlannedMealSerializer(many=True, read_only=True)
    week_end_date = serializers.DateField(read_only=True)
    grocery_list = GroceryListBasicSerializer(source='grocery_list', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    meal_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MealPlan
        fields = [
            'id', 'user', 'user_name', 'week_start_date', 'week_end_date',
            'total_cost_estimate', 'is_active', 'created_at', 'updated_at',
            'meals', 'grocery_list', 'meal_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_meal_count(self, obj):
        """Count total meals in plan"""
        return obj.meals.count()


class MealPlanBasicSerializer(serializers.ModelSerializer):
    """Minimal meal plan serializer for list views"""
    week_end_date = serializers.DateField(read_only=True)
    meal_count = serializers.IntegerField(source='meals.count', read_only=True)
    
    class Meta:
        model = MealPlan
        fields = [
            'id', 'week_start_date', 'week_end_date',
            'total_cost_estimate', 'is_active', 'meal_count'
        ]


# ========== REQUEST SERIALIZERS ==========

class CreateMealPlanSerializer(serializers.Serializer):
    """Serializer for creating a new meal plan"""
    week_start_date = serializers.DateField(required=False, allow_null=True)
    regenerate = serializers.BooleanField(default=False)
    
    def validate_week_start_date(self, value):
        """Ensure week start date is a Monday"""
        if value and value.weekday() != 0:  # 0 = Monday
            raise serializers.ValidationError("Week start date must be a Monday")
        return value


class SwapMealSerializer(serializers.Serializer):
    """Serializer for swapping a meal in a plan"""
    day_of_week = serializers.ChoiceField(choices=[0, 1, 2, 3, 4, 5, 6])
    meal_type = serializers.ChoiceField(choices=['breakfast', 'lunch', 'dinner', 'snack'])
    new_recipe_id = serializers.IntegerField(min_value=1)
    
    def validate_new_recipe_id(self, value):
        """Validate that the recipe exists"""
        if not Recipe.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipe does not exist")
        return value


class GenerateGroceryListSerializer(serializers.Serializer):
    """Serializer for triggering grocery list generation"""
    meal_plan_id = serializers.IntegerField(min_value=1)
    
    def validate_meal_plan_id(self, value):
        """Validate meal plan exists and belongs to user"""
        # This will be checked in the view with request.user
        return value
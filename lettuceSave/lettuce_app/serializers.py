from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, MealPlan, PlannedMeal, GroceryList



class RecipeBasicSerializer(serializers.ModelSerializer):
    """Minimal recipe info for meal plan display"""
    calories = serializers.ReadOnlyField()
    
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'meal_type', 'calories', 'estimated_cost']




class GroceryListSerializer(serializers.ModelSerializer):
    """Simple grocery list serializer"""
    class Meta:
        model = GroceryList
        fields = ['id', 'name', 'created_at']


# MEAL PLAN SERIALIZERS ==========

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
    week_end_date = serializers.SerializerMethodField()
    grocery_list = GroceryListSerializer(source='generated_grocery_list', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MealPlan
        fields = [
            'id', 'user', 'user_name', 'week_start_date', 'week_end_date',
            'total_cost_estimate', 'is_active', 'created_at', 'updated_at',
            'meals', 'grocery_list'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_week_end_date(self, obj):
        """Get the Sunday of the plan week"""
        return obj.week_end_date


class CreateMealPlanSerializer(serializers.Serializer):
    """Serializer for creating a new meal plan"""
    week_start_date = serializers.DateField(required=False, allow_null=True)
    regenerate = serializers.BooleanField(default=False)
    
    def validate_week_start_date(self, value):
        """Ensure week start date is a Monday (optional validation)"""
        if value and value.weekday() != 0:  # 0 = Monday
            raise serializers.ValidationError("Week start date must be a Monday")
        return value


class SwapMealSerializer(serializers.Serializer):
    """Serializer for swapping a meal in a plan"""
    day_of_week = serializers.ChoiceField(choices=[0,1,2,3,4,5,6])
    meal_type = serializers.ChoiceField(choices=['breakfast', 'lunch', 'dinner', 'snack'])
    new_recipe_id = serializers.IntegerField(min_value=1)
    
    def validate(self, data):
        """Validate that the recipe exists"""
        from .models import Recipe
        if not Recipe.objects.filter(id=data['new_recipe_id']).exists():
            raise serializers.ValidationError({
                'new_recipe_id': 'Recipe does not exist'
            })
        return data
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta

# Create your models here.

class Recipe(models.Model):
    """
    Stores a single recipe entry, related to :model:`auth.User`.
    Contains all recipe details including name, ingredients, and nutrition info.
    """
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200, help_text="Name of the recipe")
    description = models.TextField(blank=True, help_text="Brief description of the recipe")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='dinner')
    
    # Time & Difficulty
    prep_time_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    cook_time_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    
    # Nutrition (stored as JSON for flexibility)
    nutrition = models.JSONField(
        default=dict, 
        help_text="JSON data: {'calories': 450, 'protein': 25, 'carbs': 50, 'fat': 15}"
    )
    
    # Dietary tags (e.g., ['vegetarian', 'gluten-free'])
    dietary_tags = models.JSONField(default=list, help_text="List of dietary tags")
    
    # Cost & Instructions
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    instructions = models.TextField(blank=True, help_text="Step-by-step cooking instructions")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']  # Default ordering by name

    def __str__(self):
        return self.name

    @property
    def total_time_minutes(self):
        """Calculate total time (prep + cook)"""
        return (self.prep_time_minutes or 0) + (self.cook_time_minutes or 0)

    @property
    def calories(self):
        """Quick access to calories from nutrition data"""
        return self.nutrition.get('calories', 0)


class RecipeIngredient(models.Model):
    """
    Stores ingredients for a specific recipe.
    Each ingredient belongs to one recipe (ForeignKey to Recipe).
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100, help_text="Ingredient name (e.g., 'flour')")
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    metric = models.CharField(max_length=20, help_text="Unit (e.g., 'cups', 'tbsp', 'g')")
    category = models.CharField(max_length=50, blank=True, help_text="e.g., 'produce', 'dairy'")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.quantity} {self.metric} {self.name}"


class Store(models.Model):
    """
    Stores grocery store information.
    """
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    chain = models.CharField(max_length=50, blank=True, help_text="Store chain (e.g., 'Walmart')")

    def __str__(self):
        return self.name


class StoreIngredient(models.Model):
    """
    Stores pricing and availability for ingredients at specific stores.
    Used for price comparison feature.
    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    ingredient_name = models.CharField(max_length=100, db_index=True)  # Indexed for faster search
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_unit = models.CharField(max_length=20, default='each', help_text="'per lb', 'per item', etc.")
    in_stock = models.BooleanField(default=True)
    brand = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'ingredient_name', 'brand']  # Prevent duplicates
        indexes = [models.Index(fields=['store', 'in_stock'])]

    def __str__(self):
        return f"{self.ingredient_name} at {self.store.name} - ${self.price}"


class MealPlan(models.Model):
    """
    Stores a user's weekly meal plan.
    Related to :model:`auth.User` and links to a grocery list.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    week_start_date = models.DateField(help_text="Monday of the planned week")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Is this the user's current plan?")

    class Meta:
        ordering = ['-week_start_date']  # Most recent first
        unique_together = ['user', 'week_start_date', 'is_active']  # One active plan per week

    def __str__(self):
        return f"{self.user.username}'s plan for week of {self.week_start_date}"

    @property
    def week_end_date(self):
        """Calculate Sunday of the plan week"""
        return self.week_start_date + timedelta(days=6)


class PlannedMeal(models.Model):
    """
    Stores a single meal slot within a weekly meal plan.
    Links a recipe to a specific day and meal type.
    """
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    DAYS_OF_WEEK = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meals')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    custom_notes = models.TextField(blank=True, help_text="User notes for this meal")
    was_completed = models.BooleanField(default=False, help_text="Did the user actually eat this?")

    class Meta:
        unique_together = ['meal_plan', 'day_of_week', 'meal_type']  # No duplicate meals in same slot
        ordering = ['day_of_week', 'meal_type']

    def __str__(self):
        day = self.get_day_of_week_display()
        recipe_name = self.recipe.name if self.recipe else 'No recipe'
        return f"{day} {self.meal_type}: {recipe_name}"


class GroceryList(models.Model):
    """
    Stores a grocery list generated from a meal plan.
    One-to-one relationship with MealPlan.
    """
    meal_plan = models.OneToOneField(MealPlan, on_delete=models.CASCADE, related_name='grocery_list')
    name = models.CharField(max_length=100, default="My Grocery List")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Grocery list for {self.meal_plan}"


class GroceryListItem(models.Model):
    """
    Stores individual items within a grocery list.
    Each item can be linked to multiple recipes that need it.
    """
    grocery_list = models.ForeignKey(GroceryList, on_delete=models.CASCADE, related_name='items')
    ingredient_name = models.CharField(max_length=100)
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    metric = models.CharField(max_length=20)
    
    # Store and price info (from price comparison)
    suggested_store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    price_estimate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Status tracking
    is_purchased = models.BooleanField(default=False)
    
    # Track which recipes need this ingredient
    source_recipes = models.ManyToManyField(Recipe, blank=True)

    class Meta:
        ordering = ['ingredient_name']

    def __str__(self):
        return f"{self.quantity} {self.metric} {self.ingredient_name}"
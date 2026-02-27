from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

class Recipe(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='dinner')
    prep_time_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    cook_time_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    
    # Nutrition info stored as JSON for flexibility
    nutrition = models.JSONField(default=dict, help_text="Store calories, protein, carbs, fat etc.")
    
    # Dietary tags (vegetarian, vegan, gluten-free, etc.)
    dietary_tags = models.JSONField(default=list)
    
    # Estimated cost for full recipe
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Instructions
    instructions = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_time_minutes(self):
        """Calculate total time including prep and cook"""
        total = 0
        if self.prep_time_minutes:
            total += self.prep_time_minutes
        if self.cook_time_minutes:
            total += self.cook_time_minutes
        return total
    
    @property
    def calories(self):
        """Get calories from nutrition dict if available"""
        return self.nutrition.get('calories', 0)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    metric = models.CharField(max_length=20)  # e.g., 'cups', 'tbsp', 'g', 'oz'
    
    # Optional: for better matching with store items
    category = models.CharField(max_length=50, blank=True)  # e.g., 'produce', 'dairy'
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.quantity} {self.metric} {self.name}"


class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    chain = models.CharField(max_length=50, blank=True)  # e.g., 'Walmart', 'Safeway'
    
    def __str__(self):
        return self.name


class StoreIngredient(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    ingredient_name = models.CharField(max_length=100)  # Should match RecipeIngredient.name
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_unit = models.CharField(max_length=20, default='each')  # 'per lb', 'per item', etc.
    in_stock = models.BooleanField(default=True)
    brand = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['store', 'ingredient_name', 'brand']
        indexes = [
            models.Index(fields=['ingredient_name']),
            models.Index(fields=['store', 'in_stock']),
        ]
    
    def __str__(self):
        return f"{self.ingredient_name} at {self.store.name}"


class GroceryList(models.Model):
    meal_plan = models.OneToOneField(
        'MealPlan', 
        on_delete=models.CASCADE, 
        related_name='grocery_list',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100, default="My Grocery List")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def calculate_total(self):
        """Calculate total cost from all items"""
        total = sum(item.price_estimate or 0 for item in self.items.all())
        self.total_cost = total
        self.save()
        return total


class GroceryListItem(models.Model):
    grocery_list = models.ForeignKey(
        GroceryList, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    ingredient_name = models.CharField(max_length=100)
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    metric = models.CharField(max_length=20)
    
    # Store and price info
    suggested_store = models.ForeignKey(
        Store, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    price_estimate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Status
    is_purchased = models.BooleanField(default=False)
    
    # Which recipe(s) this item comes from (for tracking)
    source_recipes = models.ManyToManyField(Recipe, blank=True)
    
    class Meta:
        ordering = ['ingredient_name']
    
    def __str__(self):
        return f"{self.quantity} {self.metric} {self.ingredient_name}"





# user's Meal plan for a specific week
class MealPlan(models.Model):
    # Each meal plan belongs to one user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    # The Monday of the week this plan is for
    # Example: If planning for March 18-24, store March 18
    week_start_date = models.DateField()
    # Automatic timestamps - Django fills these in
    created_at = models.DateTimeField(auto_now_add=True)  # When plan was created
    updated_at = models.DateTimeField(auto_now=True)      # When plan was last changed
    # Estimated total cost of ALL meals in this plan
    total_cost_estimate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    # Whether this is the user's CURRENT active plan
    # A user might have old plans saved, but only one active
    is_active = models.BooleanField(default=True)
    # Link to the grocery list generated from this plan
    # One plan generates ONE grocery list
    generated_grocery_list = models.ForeignKey(
        'GroceryList', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    #-------------------------------------------------------------added
    class Meta:
        ordering = ['-week_start_date']
        unique_together = ['user', 'week_start_date', 'is_active']
    
    def __str__(self):
        return f"{self.user.username}'s plan for week of {self.week_start_date}"
    
    @property
    def week_end_date(self):
        """Get the Sunday of the plan week"""
        return self.week_start_date + timedelta(days=6)
    
    def update_cost_estimate(self):
        """Recalculate total cost from grocery list"""
        if hasattr(self, 'grocery_list') and self.grocery_list:
            self.total_cost_estimate = self.grocery_list.total_cost
            self.save()

    #--------------------------------------------------------------added


# A SINGLE meal slot in a weekly plan
class PlannedMeal(models.Model):
    # Define the possible meal types (choices)
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]
    # Define the days of week (0 = Monday for programming convenience)
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
     # Which meal plan does this belong to?
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meals')
    # Which day? (0-6)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    # Which meal type? (breakfast/lunch/dinner)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    # Which recipe is planned for this slot?
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    # Extra space for user notes
    custom_notes = models.TextField(blank=True)
    # Track if user actually ate this (for future recommendations)
    was_completed = models.BooleanField(default=False)
    
    class Meta:
        # This prevents having two meals in the same slot
        # Example: Can't have two dinners on Monday
        unique_together = ['meal_plan', 'day_of_week', 'meal_type']
        ordering = ['day_of_week', 'meal_type']
    
    def __str__(self):
        day = self.get_day_of_week_display()
        return f"{day} {self.meal_type}: {self.recipe.name if self.recipe else 'No recipe'}"
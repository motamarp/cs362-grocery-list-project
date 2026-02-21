from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta



#(testing only)
class Recipe(models.Model):
   
    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20)  # breakfast, lunch, dinner
    calories = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

#(testing only)
class GroceryList(models.Model):
    """(Simple grocery list model for meal plan testing)"""
    name = models.CharField(max_length=200, default="My Grocery List")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


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
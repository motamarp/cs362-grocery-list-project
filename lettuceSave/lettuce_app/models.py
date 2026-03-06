from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class UserProfile(models.Model):

    # user profile model containing user info
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Info
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.IntegerField(
        blank=True,
        null=True,
        help_text="Height in inches",
        validators=[MinValueValidator(36), MaxValueValidator(96)]
    )
    activity_level = models.IntegerField(
        blank=True,
        null=True,
        help_text="Your activity level on a scale of 1-5",
        validators = [MinValueValidator(1), MaxValueValidator(5)]
    )
    #Preferences
    dietary_preferences = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g, Vegetarian, Vegan, etc."
    )
    favorite_stores = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="List of favorite grocery stores (comma seperated)"
    )

    # Metadata for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['created_at']

        def __str__(self):
            return f"{self.user.username}'s Profile"
        
        @property
        def full_name(self):
            #Return user's full name
            return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username\
            
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    #Creates a UserProfile when a new User has been created
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    #Saves the UserProfile when the User is saved
    if hasattr(instance, 'profile'):
        instance.profile.save()

#recipe model to store recipes
class Recipe(models.Model):
    name = models.CharField(max_length=100)
    #can access ingredients through Recipe.RecipeIngredient_set.all()
    
    nutrition = models.IntegerField(max_length=100)

#ingredient needed in a recipe, linked to the recipe through a foreign key
class RecipeIngredient(models.Model):
    #ManytoOne relationship with Recipe, if a recipe is deleted, all its ingredients will be deleted as well
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    #name of the ingredient
    name = models.CharField(max_length=100)
    #how much of ingredient is needed (number only)
    quantity = models.FloatField()
    #unit of measurement for the ingredient
    metric = models.CharField(max_length=20)

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
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta


class Recipe(models.Model):
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

    name = models.CharField(max_length=200, help_text="Name of the recipe")
    description = models.TextField(blank=True, help_text="Brief description of the recipe")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='dinner')

    prep_time_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    cook_time_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')

    nutrition = models.JSONField(
        default=dict,
        help_text="JSON data: {'calories': 450, 'protein': 25, 'carbs': 50, 'fat': 15}"
    )

    dietary_tags = models.JSONField(default=list, help_text="List of dietary tags")

    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    instructions = models.TextField(blank=True, help_text="Step-by-step cooking instructions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_time_minutes(self):
        return (self.prep_time_minutes or 0) + (self.cook_time_minutes or 0)

    @property
    def calories(self):
        return self.nutrition.get('calories', 0)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100, help_text="Ingredient name")
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    metric = models.CharField(max_length=20, help_text="Unit")
    category = models.CharField(max_length=50, blank=True, help_text="e.g., produce, dairy")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.quantity} {self.metric} {self.name}"


class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    chain = models.CharField(max_length=50, blank=True, help_text="Store chain")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class StoreIngredient(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    ingredient_name = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_unit = models.CharField(max_length=20, default='each', help_text="'per lb', 'each', etc.")
    in_stock = models.BooleanField(default=True)
    brand = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store', 'ingredient_name', 'brand']
        indexes = [models.Index(fields=['store', 'in_stock'])]
        ordering = ['ingredient_name']

    def __str__(self):
        return f"{self.ingredient_name} at {self.store.name} - ${self.price}"


class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planner_meal_plans')
    week_start_date = models.DateField(help_text="Monday of the planned week")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Is this the user's current plan?")

    class Meta:
        ordering = ['-week_start_date']

    def __str__(self):
        return f"{self.user.username}'s plan for week of {self.week_start_date}"
    
    def update_cost_estimate(self):
        """
        Set total_cost_estimate from the associated grocery list's total_cost,
        or set to None if no grocery list exists.
        """
        if hasattr(self, 'grocery_list') and self.grocery_list:
            self.total_cost_estimate = self.grocery_list.total_cost
        else:
            self.total_cost_estimate = None
        self.save(update_fields=['total_cost_estimate'])

    @property
    def week_end_date(self):
        return self.week_start_date + timedelta(days=6)


class PlannedMeal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meals')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    custom_notes = models.TextField(blank=True, help_text="User notes for this meal")
    was_completed = models.BooleanField(default=False, help_text="Did the user actually eat this?")

    class Meta:
        unique_together = ['meal_plan', 'day_of_week', 'meal_type']
        ordering = ['day_of_week', 'meal_type']

    def __str__(self):
        day = self.get_day_of_week_display()
        recipe_name = self.recipe.name if self.recipe else 'No recipe'
        return f"{day} {self.meal_type}: {recipe_name}"


class GroceryList(models.Model):
    meal_plan = models.OneToOneField(MealPlan, on_delete=models.CASCADE, related_name='grocery_list')
    name = models.CharField(max_length=100, default="My Grocery List")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)

    def __str__(self):
        return f"Grocery list for {self.meal_plan}"

    def recalculate_total(self):
        total = sum(item.total_price for item in self.items.all())
        self.total_cost = total
        self.save(update_fields=["total_cost", "updated_at"])
        # Now update the linked meal plan's estimate
        if self.meal_plan_id:
            self.meal_plan.update_cost_estimate()

    def save(self, *args, **kwargs):
        # Save normally first (this may create or update the grocery list)
        super().save(*args, **kwargs)
        
        pass

    def delete(self, *args, **kwargs):
        # Capture the meal plan before deletion
        meal_plan = self.meal_plan if self.meal_plan_id else None
        super().delete(*args, **kwargs)
        # After deletion, update the meal plan's cost estimate (it should become None)
        if meal_plan:
            meal_plan.update_cost_estimate()


class GroceryListItem(models.Model):
    grocery_list = models.ForeignKey(GroceryList, on_delete=models.CASCADE, related_name='items')
    ingredient_name = models.CharField(max_length=100)
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    metric = models.CharField(max_length=20)

    suggested_store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    price_estimate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True)

    is_purchased = models.BooleanField(default=False)
    source_recipes = models.ManyToManyField(Recipe, blank=True)

    class Meta:
        ordering = ['ingredient_name']

    def __str__(self):
        return f"{self.quantity} {self.metric} {self.ingredient_name}"

    @property
    def total_price(self):
        if self.price_estimate is None:
            return 0
        return round(float(self.price_estimate) * float(self.quantity), 2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.grocery_list_id:
            self.grocery_list.recalculate_total()

    def delete(self, *args, **kwargs):
        grocery_list = self.grocery_list
        super().delete(*args, **kwargs)
        if grocery_list:
            grocery_list.recalculate_total()

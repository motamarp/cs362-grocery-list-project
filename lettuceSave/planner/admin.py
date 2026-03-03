from django.contrib import admin
from .models import Recipe, MealPlan, PlannedMeal, GroceryList, GroceryListItem

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'meal_type', 'difficulty')
    list_display_links = ('id', 'name') 

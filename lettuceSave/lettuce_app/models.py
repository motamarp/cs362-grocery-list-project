from django.db import models

#recipe model to store recipes
class Recipe(models.Mode):
    name = models.CharField(max_length=100)
    #can access ingredients through Recipe.RecipeIngredient_set.all()
    
    nutrition = models.ListField(IntegerField(max_length=100))

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

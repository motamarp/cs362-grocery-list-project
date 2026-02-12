from django.db import models

# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ArrayField(models.CharField(max_length=20))
    instructions = models.ArrayField(models.TextField())

class Ingredient(models.Model):
    name = models.CharField(max_length=20)
    quantity = models.CharField(max_length=20)


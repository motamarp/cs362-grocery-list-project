from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Recipe, MealPlan, GroceryList,  PlannedMeal
from .serializers import RecipeSerializer, MealPlanSerializer, GroceryListSerializer, PlannedMealSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]   # For testing only; remove in production

class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer
    permission_classes = [AllowAny]

class GroceryListViewSet(viewsets.ModelViewSet):
    queryset = GroceryList.objects.all()
    serializer_class = GroceryListSerializer
    permission_classes = [AllowAny]

class PlannedMealViewSet(viewsets.ModelViewSet):
    queryset = PlannedMeal.objects.all()
    serializer_class = PlannedMealSerializer
    permission_classes = [AllowAny]
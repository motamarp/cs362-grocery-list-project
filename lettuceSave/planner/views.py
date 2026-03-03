from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Recipe, MealPlan, GroceryList,  PlannedMeal, Store, StoreIngredient, GroceryListItem      
from .serializers import RecipeSerializer, MealPlanSerializer, GroceryListSerializer, PlannedMealSerializer, StoreSerializer, StoreIngredientSerializer, GroceryListItemSerializer  

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
    
####################################################added
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]

class StoreIngredientViewSet(viewsets.ModelViewSet):
    queryset = StoreIngredient.objects.all()
    serializer_class = StoreIngredientSerializer
    permission_classes = [AllowAny]


class GroceryListItemViewSet(viewsets.ModelViewSet):  
    queryset = GroceryListItem.objects.all()
    serializer_class = GroceryListItemSerializer
    permission_classes = [AllowAny]
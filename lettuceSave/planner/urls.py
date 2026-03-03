from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet)
router.register(r'mealplans', views.MealPlanViewSet)
router.register(r'groceries', views.GroceryListViewSet)
router.register(r'plannedmeals', views.PlannedMealViewSet)
router.register(r'stores', views.StoreViewSet)    
router.register(r'store-ingredients', views.StoreIngredientViewSet) 
router.register(r'grocery-list-items', views.GroceryListItemViewSet) 

urlpatterns = [
    path('', include(router.urls)),
]
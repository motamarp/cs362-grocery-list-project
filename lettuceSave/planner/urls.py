from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'mealplans', views.MealPlanViewSet, basename='mealplan')
router.register(r'groceries', views.GroceryListViewSet, basename='grocery')
router.register(r'plannedmeals', views.PlannedMealViewSet, basename='plannedmeal')
router.register(r'stores', views.StoreViewSet, basename='store')
router.register(r'store-ingredients', views.StoreIngredientViewSet, basename='storeingredient')
router.register(r'grocery-list-items', views.GroceryListItemViewSet, basename='grocerylistitem')


urlpatterns = [
    path('', include(router.urls)),
]

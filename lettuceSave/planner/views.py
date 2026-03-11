from urllib import request

from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .services.grocery_generator import generate_grocery_list
from .services.meal_plan_generator import generate_meal_plan


from .models import (
    Recipe,
    MealPlan,
    GroceryList,
    PlannedMeal,
    Store,
    StoreIngredient,
    GroceryListItem
)
from .serializers import (
    RecipeSerializer,
    MealPlanSerializer,
    GroceryListSerializer,
    PlannedMealSerializer,
    StoreSerializer,
    StoreIngredientSerializer,
    GroceryListItemSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]


class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user).order_by('-week_start_date')

    def perform_create(self, serializer):
        MealPlan.objects.filter(user=self.request.user, is_active=True).update(is_active=False)
        serializer.save(user=self.request.user, is_active=True)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        source_plan = self.get_object()
        new_week_start_date = request.data.get('week_start_date')

        if not new_week_start_date:
            return Response(
                {"error": "week_start_date is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        MealPlan.objects.filter(user=request.user, is_active=True).update(is_active=False)

        new_plan = MealPlan.objects.create(
            user=request.user,
            week_start_date=new_week_start_date,
            total_cost_estimate=source_plan.total_cost_estimate,
            is_active=True
        )

        source_meals = source_plan.meals.all()
        for meal in source_meals:
            PlannedMeal.objects.create(
                meal_plan=new_plan,
                day_of_week=meal.day_of_week,
                meal_type=meal.meal_type,
                recipe=meal.recipe,
                custom_notes=meal.custom_notes,
                was_completed=False
            )

        serializer = self.get_serializer(new_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        target_plan = self.get_object()
        MealPlan.objects.filter(user=request.user, is_active=True).update(is_active=False)
        target_plan.is_active = True
        target_plan.save(update_fields=['is_active', 'updated_at'])

        serializer = self.get_serializer(target_plan)
        return Response(
            {"message": "Meal plan activated.", "plan": serializer.data},
            status=status.HTTP_200_OK
        )


#added generate meal plan endpoint to MealPlanViewSet
    @action(detail=False, methods=['post'])
    def generate(self, request):
        week_start_date = request.data.get('week_start_date')

        if not week_start_date:
            return Response(
                {"error": "week_start_date is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from datetime import datetime
            week_start = datetime.strptime(week_start_date, '%Y-%m-%d').date()
            if week_start.weekday() != 0:
                return Response(
                    {"error": "week_start_date must be a Monday"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

         # Use the authenticated user from the request
        user = request.user

         # Generate the meal plan using your existing service
        from .services.meal_plan_generator import generate_meal_plan
        meal_plan = generate_meal_plan(user, week_start)


        serializer = MealPlanSerializer(meal_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


##############################################################################
    @action(detail=True, methods=['post'])
    def generate_grocery_list(self, request, pk=None):
        meal_plan = self.get_object()
        if hasattr(meal_plan, 'grocery_list') and meal_plan.grocery_list:
            return Response(
                {"error": "Grocery list already exists for this meal plan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        grocery_list = generate_grocery_list(meal_plan)
        if not grocery_list:
            return Response(
                {"error": "No ingredients found to generate grocery list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .serializers import GroceryListSerializer
        serializer = GroceryListSerializer(grocery_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class GroceryListViewSet(viewsets.ModelViewSet):
    serializer_class = GroceryListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroceryList.objects.filter(meal_plan__user=self.request.user)


class PlannedMealViewSet(viewsets.ModelViewSet):
    serializer_class = PlannedMealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlannedMeal.objects.filter(meal_plan__user=self.request.user)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]


class StoreIngredientViewSet(viewsets.ModelViewSet):
    queryset = StoreIngredient.objects.select_related('store').all()
    serializer_class = StoreIngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ingredient_name', 'brand', 'store__name']
    ordering_fields = ['price', 'ingredient_name', 'store__name']
    ordering = ['price']


class GroceryListItemViewSet(viewsets.ModelViewSet):
    serializer_class = GroceryListItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroceryListItem.objects.filter(grocery_list__meal_plan__user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_to_active_plan(self, request):
        active_plan = (
            MealPlan.objects
            .filter(user=request.user, is_active=True)
            .order_by('-week_start_date')
            .first()
        )

        if not active_plan:
            return Response(
                {"error": "No active meal plan found. Create a meal plan first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        grocery_list, _ = GroceryList.objects.get_or_create(
            meal_plan=active_plan,
            defaults={"name": f"{request.user.username}'s Grocery List"}
        )

        ingredient_name = request.data.get("ingredient_name")
        quantity = request.data.get("quantity")
        metric = request.data.get("metric", "each")
        suggested_store_id = request.data.get("suggested_store")
        price_estimate = request.data.get("price_estimate")
        brand = request.data.get("brand", "")

        if not ingredient_name or quantity in [None, ""]:
            return Response(
                {"error": "ingredient_name and quantity are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            return Response(
                {"error": "quantity must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        suggested_store = None
        if suggested_store_id:
            try:
                suggested_store = Store.objects.get(id=suggested_store_id)
            except Store.DoesNotExist:
                return Response(
                    {"error": "Suggested store not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        item, created = GroceryListItem.objects.get_or_create(
            grocery_list=grocery_list,
            ingredient_name=ingredient_name,
            metric=metric,
            suggested_store=suggested_store,
            brand=brand,
            defaults={
                "quantity": quantity,
                "price_estimate": price_estimate if price_estimate not in [None, ""] else None,
            }
        )

        if not created:
            item.quantity += quantity
            if price_estimate not in [None, ""]:
                item.price_estimate = price_estimate
            item.save()

        grocery_list.recalculate_total()
        serializer = GroceryListItemSerializer(item)

        return Response(
            {
                "message": "Item added to active meal plan grocery list.",
                "item": serializer.data,
                "meal_plan_id": active_plan.id,
                "grocery_list_id": grocery_list.id,
                "grocery_list_total": grocery_list.total_cost,
            },
            status=status.HTTP_200_OK
        )

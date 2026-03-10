from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    date_of_birth = models.DateField(blank=True, null=True)

    height = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(36), MaxValueValidator(96)]
    )

    activity_level = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    dietary_preferences = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    favorite_stores = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

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
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Recipe(models.Model):

    name = models.CharField(max_length=100)
    nutrition = models.IntegerField(null=True, blank=True)


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    quantity = models.FloatField()

    metric = models.CharField(max_length=20)


class GroceryList(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class MealPlan(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lettuce_meal_plans')

    week_start_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    total_cost_estimate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    generated_grocery_list = models.ForeignKey(
        GroceryList,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

class PlannedMeal(models.Model):

    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
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

    custom_notes = models.TextField(blank=True)

    was_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['meal_plan', 'day_of_week', 'meal_type']

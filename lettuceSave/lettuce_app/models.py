from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):

    # user profile model containing user info
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Info
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.IntegerField(
        blank=True,
        null=True,
        help_text="Height in inches"
    )
    
    # Preferences
    dietary_preferences = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="e.g., Vegetarian, Vegan, Gluten-free"
    )
    favorite_stores = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="List of favorite grocery stores (comma seperated)"
    )
    
    # Metadata for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        #Return user's full name
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    #Creates a UserProfile when a new User has been created
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    #Saves the UserProfile when the User is saved
    if hasattr(instance, 'profile'):
        instance.profile.save()
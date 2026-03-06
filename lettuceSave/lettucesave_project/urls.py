"""
URL configuration for lettucesave_project project.
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lettuce_app.views import (
    UserRegistrationView,
    UserProfileViewSet
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('lettuce_app.urls')),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('', include(router.urls)),
    path('planner/', include('planner.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

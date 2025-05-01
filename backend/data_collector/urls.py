from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
# Add data collector viewsets here

urlpatterns = [
    path('', include(router.urls)),
    # Add other data collector specific URLs here
] 
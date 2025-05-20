from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'threads', views.ChatThreadViewSet, basename='chat-thread')
router.register(r'messages', views.ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
] 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, WorkflowTaskViewSet

router = DefaultRouter()
router.register(r'input-collections', WorkflowViewSet, basename='input-collection')
router.register(r'workflow-tasks', WorkflowTaskViewSet, basename='workflow-task')

urlpatterns = [
    path('', include(router.urls)),
] 
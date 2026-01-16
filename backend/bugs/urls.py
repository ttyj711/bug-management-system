from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BugViewSet

router = DefaultRouter()
router.register('', BugViewSet, basename='bug')

urlpatterns = [
    path('', include(router.urls)),
]

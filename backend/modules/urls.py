from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProductViewSet, ModuleViewSet, ModuleCascadeView

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('products', ProductViewSet, basename='product')
router.register('modules', ModuleViewSet, basename='module')

urlpatterns = [
    path('cascade/', ModuleCascadeView.as_view(), name='module_cascade'),
    path('', include(router.urls)),
]

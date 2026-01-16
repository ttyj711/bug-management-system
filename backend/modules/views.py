from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, Product, Module
from .serializers import (
    ProjectSerializer, ProductSerializer, ModuleSerializer,
    ProjectCascadeSerializer
)


class IsSuperAdmin(permissions.BasePermission):
    """超级管理员权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class ProjectViewSet(viewsets.ModelViewSet):
    """项目管理"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Project.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """产品管理"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Product.objects.select_related('project').prefetch_related('modules')
        project = self.request.query_params.get('project')
        is_active = self.request.query_params.get('is_active')
        if project:
            queryset = queryset.filter(project_id=project)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class ModuleViewSet(viewsets.ModelViewSet):
    """模块管理"""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Module.objects.select_related('product', 'product__project')
        product = self.request.query_params.get('product')
        is_active = self.request.query_params.get('is_active')
        if product:
            queryset = queryset.filter(product_id=product)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class ModuleCascadeView(APIView):
    """获取模块级联数据（项目-产品-模块）"""
    
    def get(self, request):
        projects = Project.objects.filter(is_active=True).prefetch_related(
            'products__modules'
        )
        serializer = ProjectCascadeSerializer(projects, many=True)
        return Response(serializer.data)

"""
模块管理 - 视图层
处理项目-产品-模块三级层级结构的CRUD操作和级联数据获取
"""
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
    """
    超级管理员权限类
    
    仅允许角色为super_admin的已认证用户访问
    用于保护模块管理等高级功能
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集
    
    接口：
    - GET /api/modules/projects/ - 获取项目列表
    - POST /api/modules/projects/ - 创建项目（仅超管）
    - GET /api/modules/projects/{id}/ - 获取项目详情
    - PUT/PATCH /api/modules/projects/{id}/ - 更新项目（仅超管）
    - DELETE /api/modules/projects/{id}/ - 删除项目（仅超管）
    
    查询参数：
    - is_active: 'true'/'false' 按启用状态筛选
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_permissions(self):
        """写操作仅超管可执行，读操作需登录"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """支持按启用状态筛选"""
        queryset = Project.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    产品管理视图集
    
    接口：
    - GET /api/modules/products/ - 获取产品列表
    - POST /api/modules/products/ - 创建产品（仅超管）
    - GET /api/modules/products/{id}/ - 获取产品详情
    - PUT/PATCH /api/modules/products/{id}/ - 更新产品（仅超管）
    - DELETE /api/modules/products/{id}/ - 删除产品（仅超管）
    
    查询参数：
    - project: 按所属项目ID筛选
    - is_active: 'true'/'false' 按启用状态筛选
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        """写操作仅超管可执行，读操作需登录"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        获取产品查询集
        - 使用select_related优化项目关联查询
        - 使用prefetch_related预加载模块列表
        - 支持按项目和启用状态筛选
        """
        queryset = Product.objects.select_related('project').prefetch_related('modules')
        project = self.request.query_params.get('project')
        is_active = self.request.query_params.get('is_active')
        if project:
            queryset = queryset.filter(project_id=project)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class ModuleViewSet(viewsets.ModelViewSet):
    """
    功能模块管理视图集
    
    接口：
    - GET /api/modules/modules/ - 获取模块列表
    - POST /api/modules/modules/ - 创建模块（仅超管）
    - GET /api/modules/modules/{id}/ - 获取模块详情
    - PUT/PATCH /api/modules/modules/{id}/ - 更新模块（仅超管）
    - DELETE /api/modules/modules/{id}/ - 删除模块（仅超管）
    
    查询参数：
    - product: 按所属产品ID筛选
    - is_active: 'true'/'false' 按启用状态筛选
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    
    def get_permissions(self):
        """写操作仅超管可执行，读操作需登录"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        获取模块查询集
        - 使用select_related优化产品和项目关联查询
        - 支持按产品和启用状态筛选
        """
        queryset = Module.objects.select_related('product', 'product__project')
        product = self.request.query_params.get('product')
        is_active = self.request.query_params.get('is_active')
        if product:
            queryset = queryset.filter(product_id=product)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class ModuleCascadeView(APIView):
    """
    获取模块级联数据视图
    
    接口：GET /api/modules/cascade/
    
    功能：返回项目-产品-模块的完整层级结构数据
    用途：前端BUG提报表单中的级联选择器使用
    
    返回格式：
    [
        {
            "value": 1,           # 项目ID
            "label": "项目名称",
            "children": [
                {
                    "value": 1,   # 产品ID
                    "label": "产品名称",
                    "children": [
                        {
                            "value": 1,  # 模块ID
                            "label": "模块名称"
                        }
                    ]
                }
            ]
        }
    ]
    
    注意：
    - 只返回启用状态(is_active=True)的数据
    - 使用prefetch_related优化查询性能
    """
    
    def get(self, request):
        # 查询所有启用的项目，并预加载产品和模块
        projects = Project.objects.filter(is_active=True).prefetch_related(
            'products__modules'
        )
        # 使用级联序列化器构建层级结构
        serializer = ProjectCascadeSerializer(projects, many=True)
        return Response(serializer.data)

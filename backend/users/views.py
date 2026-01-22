"""
用户模块 - 视图层
处理用户相关的所有HTTP请求，包括认证、用户管理、个人信息等
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordResetSerializer, LoginSerializer, UserProfileSerializer
)

# 获取自定义用户模型
User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    """
    超级管理员权限类
    
    仅允许角色为super_admin的已认证用户访问
    用于保护需要最高权限的操作，如用户管理、系统配置等
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsAdminUser(permissions.BasePermission):
    """
    管理员权限类
    
    允许超级管理员或普通管理员访问
    用于保护需要管理员权限的操作，如BUG分配等
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class LoginView(APIView):
    """
    用户登录视图
    
    接口：POST /api/users/login/
    功能：验证用户凭证，返回JWT令牌
    
    请求参数：
    - username: 用户名
    - password: 密码
    
    返回数据：
    - access: JWT访问令牌（用于API认证）
    - refresh: JWT刷新令牌（用于获取新的访问令牌）
    - user: 用户基本信息
    """
    permission_classes = [permissions.AllowAny]  # 允许匿名访问
    
    def post(self, request):
        # 验证请求数据格式
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 使用Django内置认证验证用户名密码
        user = authenticate(username=username, password=password)
        
        # 验证失败
        if user is None:
            return Response({'detail': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 检查用户是否被禁用
        if user.status == 'disabled':
            return Response({'detail': '账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """
    用户登出视图
    
    接口：POST /api/users/logout/
    功能：将refresh令牌加入黑名单，使其失效
    
    请求参数：
    - refresh: JWT刷新令牌
    """
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # 将令牌加入黑名单
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # 即使失败也返回成功，避免泄露信息
        return Response({'detail': '登出成功'})


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    
    提供用户的CRUD操作：
    - GET /api/users/ - 获取用户列表
    - POST /api/users/ - 创建用户（仅超管）
    - GET /api/users/{id}/ - 获取用户详情
    - PUT/PATCH /api/users/{id}/ - 更新用户信息（仅超管）
    - DELETE /api/users/{id}/ - 删除用户（仅超管）
    
    扩展操作：
    - POST /api/users/{id}/reset_password/ - 重置用户密码
    - POST /api/users/{id}/toggle_status/ - 切换用户启用/禁用状态
    
    查询参数：
    - role: 按角色筛选
    - status: 按状态筛选
    - search: 按用户名搜索
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """根据操作类型选择不同的序列化器"""
        if self.action == 'create':
            return UserCreateSerializer  # 创建用户时需要密码
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer  # 更新用户时不需要密码
        return UserSerializer  # 其他操作使用基础序列化器
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]  # 创建和删除只有超管可操作
        elif self.action in ['update', 'partial_update', 'list', 'retrieve']:
            return [IsSuperAdmin()]  # 修改和查看也限制为超管
        return [permissions.IsAuthenticated()]  # 默认需要登录
    
    def get_queryset(self):
        """
        获取用户列表查询集
        支持多条件筛选
        """
        queryset = User.objects.all()
        
        # 从URL参数获取筛选条件
        role = self.request.query_params.get('role')
        status_param = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        # 应用筛选条件
        if role:
            queryset = queryset.filter(role=role)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if search:
            queryset = queryset.filter(username__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reset_password(self, request, pk=None):
        """
        管理员重置用户密码
        
        接口：POST /api/users/{id}/reset_password/
        权限：仅超级管理员
        
        请求参数：
        - new_password: 新密码
        """
        user = self.get_object()
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 设置新密码（会自动加密）
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': '密码重置成功'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def toggle_status(self, request, pk=None):
        """
        切换用户启用/禁用状态
        
        接口：POST /api/users/{id}/toggle_status/
        权限：仅超级管理员
        
        功能：如果用户是启用状态则禁用，反之则启用
        """
        user = self.get_object()
        # 状态切换
        user.status = 'disabled' if user.status == 'active' else 'active'
        user.save()
        return Response({'detail': '状态更新成功', 'status': user.status})


class ProfileView(APIView):
    """
    个人信息管理视图
    
    接口：
    - GET /api/users/profile/ - 获取当前登录用户信息
    - PUT /api/users/profile/ - 更新当前登录用户信息
    """
    
    def get(self, request):
        """获取个人信息"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """更新个人信息（部分更新）"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    修改个人密码视图
    
    接口：POST /api/users/change-password/
    
    请求参数：
    - old_password: 原密码
    - new_password: 新密码
    """
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data.get('old_password')
        
        # 验证原密码是否正确
        if not user.check_password(old_password):
            return Response({'detail': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': '密码修改成功'})


class DeveloperListView(APIView):
    """
    获取开发人员列表视图
    
    接口：GET /api/users/developers/
    功能：返回所有启用状态的开发人员列表
    用途：BUG分配时选择处理人
    """
    
    def get(self, request):
        # 筛选角色为开发人员且状态为启用的用户
        developers = User.objects.filter(role='developer', status='active')
        serializer = UserSerializer(developers, many=True)
        return Response(serializer.data)

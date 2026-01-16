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

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    """超级管理员权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsAdminUser(permissions.BasePermission):
    """管理员权限（超级管理员或普通管理员）"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class LoginView(APIView):
    """用户登录"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({'detail': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.status == 'disabled':
            return Response({'detail': '账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """用户登出"""
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'detail': '登出成功'})


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        elif self.action in ['update', 'partial_update', 'list', 'retrieve']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # 筛选条件
        role = self.request.query_params.get('role')
        status_param = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if search:
            queryset = queryset.filter(username__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reset_password(self, request, pk=None):
        """管理员重置用户密码"""
        user = self.get_object()
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': '密码重置成功'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def toggle_status(self, request, pk=None):
        """切换用户状态"""
        user = self.get_object()
        user.status = 'disabled' if user.status == 'active' else 'active'
        user.save()
        return Response({'detail': '状态更新成功', 'status': user.status})


class ProfileView(APIView):
    """个人信息管理"""
    
    def get(self, request):
        """获取个人信息"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """更新个人信息"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """修改个人密码"""
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data.get('old_password')
        
        if not user.check_password(old_password):
            return Response({'detail': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': '密码修改成功'})


class DeveloperListView(APIView):
    """获取开发人员列表（用于BUG分配）"""
    
    def get(self, request):
        developers = User.objects.filter(role='developer', status='active')
        serializer = UserSerializer(developers, many=True)
        return Response(serializer.data)

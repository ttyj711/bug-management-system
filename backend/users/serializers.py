"""
用户模块 - 序列化器
定义用户数据的序列化和反序列化规则，用于API的数据验证和转换
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# 获取自定义用户模型
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    用户基础序列化器
    
    用于用户列表和详情展示，包含所有基本字段
    同时提供角色和状态的中文显示字段
    """
    # 角色中文显示（如 "超级管理员"）
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    # 状态中文显示（如 "启用"）
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role', 'role_display',
            'status', 'status_display', 'avatar', 'is_active', 
            'created_at', 'updated_at'
        ]
        # 只读字段，不允许通过API修改
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器
    
    用于创建新用户，包含密码字段的处理
    - 密码使用Django内置的密码验证器进行强度验证
    - 需要二次确认密码
    - 密码会被加密存储
    """
    # 密码字段，只写不读，使用Django密码验证器
    password = serializers.CharField(write_only=True, validators=[validate_password])
    # 确认密码字段
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password', 'confirm_password', 'role', 'status']
    
    def validate(self, attrs):
        """验证两次密码输入是否一致"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        return attrs
    
    def create(self, validated_data):
        """
        创建用户
        - 移除确认密码字段
        - 使用set_password加密密码
        """
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # 加密密码
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器
    
    用于更新用户信息，不包含密码字段
    密码修改通过单独的接口处理
    """
    
    class Meta:
        model = User
        fields = ['email', 'phone', 'role', 'status']


class PasswordResetSerializer(serializers.Serializer):
    """
    密码重置/修改序列化器
    
    用于两种场景：
    1. 用户自己修改密码：需要提供old_password
    2. 管理员重置密码：不需要old_password
    """
    # 原密码（用户自己修改时需要）
    old_password = serializers.CharField(required=False)
    # 新密码（使用Django密码验证器）
    new_password = serializers.CharField(validators=[validate_password])
    # 确认新密码
    confirm_password = serializers.CharField()
    
    def validate(self, attrs):
        """验证两次新密码输入是否一致"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        return attrs


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    
    用于验证登录请求的数据格式
    """
    username = serializers.CharField()  # 用户名
    password = serializers.CharField()  # 密码


class UserProfileSerializer(serializers.ModelSerializer):
    """
    个人信息序列化器
    
    用于用户查看和修改自己的个人信息
    部分字段（如用户名、角色）不允许自行修改
    """
    # 角色中文显示
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'role_display', 'avatar']
        # 用户名和角色不允许自行修改
        read_only_fields = ['id', 'username', 'role']

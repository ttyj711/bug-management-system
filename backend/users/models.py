"""
用户模块 - 数据模型
定义系统用户模型，支持角色权限管理
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    自定义用户模型
    
    继承Django内置的AbstractUser，扩展以下功能：
    - 角色管理：支持超级管理员、普通管理员、测试人员、开发人员四种角色
    - 状态管理：支持启用/禁用用户
    - 附加信息：手机号、头像等
    
    权限说明：
    - super_admin: 拥有所有权限，可管理用户、模块、查看所有BUG
    - admin: 可管理用户（除超管外）、查看所有BUG
    - tester: 可提报BUG、查看自己创建的BUG
    - developer: 可处理分配给自己的BUG、查看相关BUG
    """
    
    # 角色选项定义
    ROLE_CHOICES = (
        ('super_admin', '超级管理员'),  # 最高权限，可管理系统所有功能
        ('admin', '普通管理员'),         # 可管理用户和查看所有BUG
        ('tester', '测试人员'),          # 可提报和跟踪BUG
        ('developer', '开发人员'),       # 可处理分配的BUG
    )
    
    # 用户状态选项
    STATUS_CHOICES = (
        ('active', '启用'),    # 用户可正常登录使用系统
        ('disabled', '禁用'),  # 用户被禁用，无法登录
    )
    
    # 用户角色字段
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='tester')
    # 用户状态字段
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    # 手机号（可选）
    phone = models.CharField('手机号', max_length=20, blank=True, default='')
    # 用户头像（可选）
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    # 创建时间（自动记录）
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间（自动更新）
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'  # 数据库表名
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']  # 按创建时间倒序排列

    def __str__(self):
        """返回用户名作为字符串表示"""
        return self.username
    
    @property
    def is_super_admin(self):
        """判断是否为超级管理员"""
        return self.role == 'super_admin'
    
    @property
    def is_admin(self):
        """判断是否为管理员（包括超级管理员和普通管理员）"""
        return self.role in ('super_admin', 'admin')
    
    @property
    def is_tester(self):
        """判断是否为测试人员"""
        return self.role == 'tester'
    
    @property
    def is_developer(self):
        """判断是否为开发人员"""
        return self.role == 'developer'

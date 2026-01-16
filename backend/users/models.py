from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型"""
    
    ROLE_CHOICES = (
        ('super_admin', '超级管理员'),
        ('admin', '普通管理员'),
        ('tester', '测试人员'),
        ('developer', '开发人员'),
    )
    
    STATUS_CHOICES = (
        ('active', '启用'),
        ('disabled', '禁用'),
    )
    
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='tester')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    phone = models.CharField('手机号', max_length=20, blank=True, default='')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.username
    
    @property
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def is_admin(self):
        return self.role in ('super_admin', 'admin')
    
    @property
    def is_tester(self):
        return self.role == 'tester'
    
    @property
    def is_developer(self):
        return self.role == 'developer'

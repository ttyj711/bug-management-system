#!/usr/bin/env python
"""
创建测试用户脚本
用于快速创建一个可用于登录的测试用户
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user():
    """创建测试用户"""
    # 检查是否已有测试用户
    username = "testadmin"
    email = "admin@example.com"
    password = "admin123"
    
    if User.objects.filter(username=username).exists():
        print(f"用户 {username} 已存在")
        user = User.objects.get(username=username)
        print(f"用户ID: {user.id}")
        print(f"角色: {user.get_role_display()}")
        print(f"状态: {user.get_status_display()}")
        print(f"邮箱: {user.email}")
        return
    
    # 创建新的测试用户
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role="super_admin",
        status="active"
    )
    
    print(f"测试用户创建成功!")
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print(f"邮箱: {email}")
    print(f"角色: {user.get_role_display()}")
    print(f"状态: {user.get_status_display()}")
    print(f"\n请使用以上信息登录系统")

if __name__ == "__main__":
    create_test_user()

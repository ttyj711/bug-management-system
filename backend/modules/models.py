"""
模块管理 - 数据模型
定义项目-产品-模块三级层级结构，用于BUG的精确归属

层级关系：
Project (项目)
  └── Product (产品)
        └── Module (功能模块)

示例：
电商平台（项目）
  ├── 用户中心（产品）
  │     ├── 用户注册（模块）
  │     ├── 用户登录（模块）
  │     └── 密码找回（模块）
  └── 商品管理（产品）
        ├── 商品列表（模块）
        └── 购物车（模块）
"""
from django.db import models


class Project(models.Model):
    """
    项目模型
    
    最顶层的组织单位，代表一个独立的软件项目
    一个项目可以包含多个产品
    """
    # 项目名称
    name = models.CharField('项目名称', max_length=100)
    # 项目描述（可选）
    description = models.TextField('描述', blank=True, default='')
    # 是否启用（禁用后在级联选择中不显示）
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'projects'  # 数据库表名
        verbose_name = '项目'
        verbose_name_plural = verbose_name
        ordering = ['name']  # 按名称排序

    def __str__(self):
        """返回项目名称"""
        return self.name


class Product(models.Model):
    """
    产品模型
    
    项目下的子分类，代表项目中的一个产品或子系统
    一个产品可以包含多个功能模块
    """
    # 所属项目（外键关联）
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,  # 项目删除时，产品也删除
        related_name='products',   # 反向查询：project.products.all()
        verbose_name='所属项目'
    )
    # 产品名称
    name = models.CharField('产品名称', max_length=100)
    # 产品描述（可选）
    description = models.TextField('描述', blank=True, default='')
    # 是否启用
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'products'  # 数据库表名
        verbose_name = '产品'
        verbose_name_plural = verbose_name
        ordering = ['name']  # 按名称排序

    def __str__(self):
        """返回 项目名-产品名 格式"""
        return f"{self.project.name} - {self.name}"


class Module(models.Model):
    """
    功能模块模型
    
    产品下的具体功能点，是BUG归属的最小单位
    BUG提报时通过级联选择器关联到具体的模块
    """
    # 所属产品（外键关联）
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,  # 产品删除时，模块也删除
        related_name='modules',    # 反向查询：product.modules.all()
        verbose_name='所属产品'
    )
    # 模块名称
    name = models.CharField('模块名称', max_length=100)
    # 模块描述（可选）
    description = models.TextField('描述', blank=True, default='')
    # 是否启用
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'modules'  # 数据库表名
        verbose_name = '功能模块'
        verbose_name_plural = verbose_name
        ordering = ['name']  # 按名称排序

    def __str__(self):
        """返回完整路径：项目名-产品名-模块名"""
        return f"{self.product.project.name} - {self.product.name} - {self.name}"

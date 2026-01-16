from django.db import models


class Project(models.Model):
    """项目"""
    name = models.CharField('项目名称', max_length=100)
    description = models.TextField('描述', blank=True, default='')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'projects'
        verbose_name = '项目'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """产品"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='products', verbose_name='所属项目')
    name = models.CharField('产品名称', max_length=100)
    description = models.TextField('描述', blank=True, default='')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = '产品'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Module(models.Model):
    """功能模块"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='modules', verbose_name='所属产品')
    name = models.CharField('模块名称', max_length=100)
    description = models.TextField('描述', blank=True, default='')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'modules'
        verbose_name = '功能模块'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return f"{self.product.project.name} - {self.product.name} - {self.name}"

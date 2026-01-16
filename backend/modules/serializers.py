from rest_framework import serializers
from .models import Project, Product, Module


class ModuleSerializer(serializers.ModelSerializer):
    """模块序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'product', 'product_name', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """产品序列化器"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'project', 'project_name', 'name', 'description', 'is_active', 'modules', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSimpleSerializer(serializers.ModelSerializer):
    """产品简单序列化器"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'is_active']


class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器"""
    products = ProductSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'is_active', 'products', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectSimpleSerializer(serializers.ModelSerializer):
    """项目简单序列化器"""
    class Meta:
        model = Project
        fields = ['id', 'name', 'is_active']


class ModuleCascadeSerializer(serializers.ModelSerializer):
    """模块级联序列化器（用于BUG提报时的级联选择）"""
    label = serializers.CharField(source='name')
    value = serializers.IntegerField(source='id')
    
    class Meta:
        model = Module
        fields = ['value', 'label']


class ProductCascadeSerializer(serializers.ModelSerializer):
    """产品级联序列化器"""
    label = serializers.CharField(source='name')
    value = serializers.IntegerField(source='id')
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['value', 'label', 'children']
    
    def get_children(self, obj):
        modules = obj.modules.filter(is_active=True)
        return ModuleCascadeSerializer(modules, many=True).data


class ProjectCascadeSerializer(serializers.ModelSerializer):
    """项目级联序列化器"""
    label = serializers.CharField(source='name')
    value = serializers.IntegerField(source='id')
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['value', 'label', 'children']
    
    def get_children(self, obj):
        products = obj.products.filter(is_active=True)
        return ProductCascadeSerializer(products, many=True).data

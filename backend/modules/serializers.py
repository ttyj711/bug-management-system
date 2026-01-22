"""
模块管理 - 序列化器
定义项目-产品-模块层级数据的序列化规则
包括基础序列化器和级联选择器专用序列化器
"""
from rest_framework import serializers
from .models import Project, Product, Module


class ModuleSerializer(serializers.ModelSerializer):
    """
    模块序列化器
    
    用于模块的CRUD操作，包含所属产品名称
    """
    # 所属产品名称（只读）
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'product', 'product_name', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """
    产品序列化器
    
    用于产品的CRUD操作，包含所属项目名称和模块列表
    """
    # 所属项目名称（只读）
    project_name = serializers.CharField(source='project.name', read_only=True)
    # 包含的模块列表（嵌套序列化）
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'project', 'project_name', 'name', 'description', 'is_active', 'modules', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSimpleSerializer(serializers.ModelSerializer):
    """
    产品简单序列化器
    
    只包含基本字段，用于项目列表中嵌套显示
    不包含模块列表，减少数据量
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'is_active']


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目序列化器
    
    用于项目的CRUD操作，包含产品列表（简化版）
    """
    # 包含的产品列表（使用简单序列化器）
    products = ProductSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'is_active', 'products', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectSimpleSerializer(serializers.ModelSerializer):
    """
    项目简单序列化器
    
    只包含基本字段，用于下拉选择等场景
    """
    class Meta:
        model = Project
        fields = ['id', 'name', 'is_active']


# ============ 级联选择器专用序列化器 ============
# 以下序列化器用于前端级联选择器（el-cascader）组件
# 输出格式：{ value: id, label: name, children: [...] }


class ModuleCascadeSerializer(serializers.ModelSerializer):
    """
    模块级联序列化器
    
    用于BUG提报时的级联选择器，最底层节点
    输出格式：{ value: 模块ID, label: 模块名称 }
    """
    # Element Plus级联选择器需要的字段名
    label = serializers.CharField(source='name')  # 显示文本
    value = serializers.IntegerField(source='id')  # 选中值
    
    class Meta:
        model = Module
        fields = ['value', 'label']


class ProductCascadeSerializer(serializers.ModelSerializer):
    """
    产品级联序列化器
    
    用于级联选择器的中间层，包含模块子节点
    输出格式：{ value: 产品ID, label: 产品名称, children: [模块...] }
    """
    # Element Plus级联选择器需要的字段名
    label = serializers.CharField(source='name')  # 显示文本
    value = serializers.IntegerField(source='id')  # 选中值
    # 子节点（模块列表）
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['value', 'label', 'children']
    
    def get_children(self, obj):
        """
        获取该产品下所有启用的模块
        只返回is_active=True的模块
        """
        modules = obj.modules.filter(is_active=True)
        return ModuleCascadeSerializer(modules, many=True).data


class ProjectCascadeSerializer(serializers.ModelSerializer):
    """
    项目级联序列化器
    
    用于级联选择器的顶层，包含产品子节点
    输出格式：{ value: 项目ID, label: 项目名称, children: [产品...] }
    
    完整数据结构示例：
    [
        {
            "value": 1,
            "label": "电商平台",
            "children": [
                {
                    "value": 1,
                    "label": "用户中心",
                    "children": [
                        { "value": 1, "label": "用户注册" },
                        { "value": 2, "label": "用户登录" }
                    ]
                }
            ]
        }
    ]
    """
    # Element Plus级联选择器需要的字段名
    label = serializers.CharField(source='name')  # 显示文本
    value = serializers.IntegerField(source='id')  # 选中值
    # 子节点（产品列表）
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['value', 'label', 'children']
    
    def get_children(self, obj):
        """
        获取该项目下所有启用的产品
        只返回is_active=True的产品
        """
        products = obj.products.filter(is_active=True)
        return ProductCascadeSerializer(products, many=True).data

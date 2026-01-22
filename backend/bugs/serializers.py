"""
BUG模块 - 序列化器
定义BUG数据的序列化和反序列化规则，支持列表、详情、创建、更新等场景
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Bug, BugAttachment

# 获取自定义用户模型
User = get_user_model()


class BugAttachmentSerializer(serializers.ModelSerializer):
    """
    BUG附件序列化器
    
    用于附件信息的展示，包含文件URL和上传时间
    """
    
    class Meta:
        model = BugAttachment
        fields = ['id', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']


class BugListSerializer(serializers.ModelSerializer):
    """
    BUG列表序列化器
    
    用于BUG列表页展示，包含必要的字段和关联数据
    - 提供创建人和处理人的用户名
    - 提供各字段的中文显示值
    - 提供模块的完整路径
    """
    # 创建人用户名
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    # 处理人用户名（可能为空）
    assignee_name = serializers.CharField(source='assignee.username', read_only=True, default='')
    # 严重程度中文显示
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    # 优先级中文显示
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    # 状态中文显示
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # 模块完整路径（项目/产品/模块）
    module_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Bug
        fields = [
            'id', 'title', 'severity', 'severity_display', 'priority', 'priority_display',
            'status', 'status_display', 'module', 'module_path', 'version',
            'creator', 'creator_name', 'assignee', 'assignee_name',
            'created_at', 'updated_at'
        ]
    
    def get_module_path(self, obj):
        """
        获取模块完整路径
        格式：项目名 / 产品名 / 模块名
        """
        if obj.module:
            return f"{obj.module.product.project.name} / {obj.module.product.name} / {obj.module.name}"
        return ''


class BugDetailSerializer(serializers.ModelSerializer):
    """
    BUG详情序列化器
    
    用于BUG详情页展示，包含完整的BUG信息
    - 包含所有基础字段和关联数据
    - 包含附件列表
    - 包含模块级联选择数据（用于编辑时回显）
    """
    # 创建人用户名
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    # 处理人用户名
    assignee_name = serializers.CharField(source='assignee.username', read_only=True, default='')
    # 严重程度中文显示
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    # 优先级中文显示
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    # 状态中文显示
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # 附件列表（嵌套序列化）
    attachments = BugAttachmentSerializer(many=True, read_only=True)
    # 模块完整路径
    module_path = serializers.SerializerMethodField()
    # 模块级联值数组（用于编辑时填充级联选择器）
    module_cascade = serializers.SerializerMethodField()
    
    class Meta:
        model = Bug
        fields = [
            'id', 'title', 'description', 'severity', 'severity_display',
            'priority', 'priority_display', 'status', 'status_display',
            'module', 'module_path', 'module_cascade', 'version', 'creator', 'creator_name',
            'assignee', 'assignee_name', 'solution', 'reject_reason',
            'attachments', 'created_at', 'updated_at'
        ]
    
    def get_module_path(self, obj):
        """获取模块完整路径"""
        if obj.module:
            return f"{obj.module.product.project.name} / {obj.module.product.name} / {obj.module.name}"
        return ''
    
    def get_module_cascade(self, obj):
        """
        返回级联选择器的值数组
        格式：[project_id, product_id, module_id]
        用于编辑BUG时回显级联选择器的选中状态
        """
        if obj.module:
            return [obj.module.product.project.id, obj.module.product.id, obj.module.id]
        return []


class BugCreateSerializer(serializers.ModelSerializer):
    """
    BUG创建序列化器
    
    用于创建新BUG，支持同时上传多个附件
    - 自动设置创建人为当前登录用户
    - 附件作为列表字段处理
    """
    # 附件列表（可选，支持多文件上传）
    attachments = serializers.ListField(
        child=serializers.ImageField(), 
        write_only=True, 
        required=False
    )
    
    class Meta:
        model = Bug
        fields = [
            'title', 'description', 'severity', 'priority',
            'module', 'version', 'assignee', 'attachments'
        ]
    
    def create(self, validated_data):
        """
        创建BUG
        - 提取附件列表
        - 设置创建人为当前用户
        - 创建BUG记录
        - 创建附件记录
        """
        attachments = validated_data.pop('attachments', [])
        # 从请求上下文获取当前用户作为创建人
        validated_data['creator'] = self.context['request'].user
        bug = Bug.objects.create(**validated_data)
        
        # 创建附件记录
        for attachment in attachments:
            BugAttachment.objects.create(bug=bug, file=attachment)
        
        return bug


class BugUpdateSerializer(serializers.ModelSerializer):
    """
    BUG更新序列化器
    
    用于更新BUG信息，支持追加附件
    - 新上传的附件会追加到现有附件列表
    - 删除附件需要通过单独的接口
    """
    # 附件列表（可选，新上传的附件）
    attachments = serializers.ListField(
        child=serializers.ImageField(), 
        write_only=True, 
        required=False
    )
    
    class Meta:
        model = Bug
        fields = [
            'title', 'description', 'severity', 'priority',
            'module', 'version', 'assignee', 'attachments'
        ]
    
    def update(self, instance, validated_data):
        """
        更新BUG
        - 提取附件列表
        - 更新BUG基础字段
        - 追加新附件
        """
        attachments = validated_data.pop('attachments', [])
        
        # 更新BUG字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 追加新附件
        for attachment in attachments:
            BugAttachment.objects.create(bug=instance, file=attachment)
        
        return instance


class BugStatusUpdateSerializer(serializers.Serializer):
    """
    BUG状态更新序列化器
    
    用于BUG状态流转，包含状态及相关说明字段
    - 状态改为resolved时必须填写解决说明
    - 状态改为rejected时必须填写驳回原因
    """
    # 新状态（必须是有效的状态值）
    status = serializers.ChoiceField(choices=Bug.STATUS_CHOICES)
    # 解决说明（状态为resolved时必填）
    solution = serializers.CharField(required=False, allow_blank=True)
    # 驳回原因（状态为rejected时必填）
    reject_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """
        验证状态相关字段
        - 解决时必须填写解决说明
        - 驳回时必须填写驳回原因
        """
        status = attrs.get('status')
        if status == 'resolved' and not attrs.get('solution'):
            raise serializers.ValidationError({'solution': '解决BUG时必须填写解决说明'})
        if status == 'rejected' and not attrs.get('reject_reason'):
            raise serializers.ValidationError({'reject_reason': '驳回BUG时必须填写驳回原因'})
        return attrs

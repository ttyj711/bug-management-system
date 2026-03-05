"""
BUG模块 - 序列化器
定义BUG数据的序列化和反序列化规则，支持列表、详情、创建、更新等场景
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Bug, BugAttachment, BugHistory

User = get_user_model()


class BugAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugAttachment
        fields = ['id', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']


class BugHistorySerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = BugHistory
        fields = [
            'id', 'operator', 'operator_name', 'action', 'action_display',
            'field_name', 'old_value', 'new_value', 'description', 'created_at'
        ]


class BugListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True, default='')
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
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
        if obj.module:
            return f"{obj.module.product.project.name} / {obj.module.product.name} / {obj.module.name}"
        return ''


class BugDetailSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True, default='')
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    attachments = BugAttachmentSerializer(many=True, read_only=True)
    module_path = serializers.SerializerMethodField()
    module_cascade = serializers.SerializerMethodField()
    history = BugHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Bug
        fields = [
            'id', 'title', 'description', 'severity', 'severity_display',
            'priority', 'priority_display', 'status', 'status_display',
            'module', 'module_path', 'module_cascade', 'version', 'creator', 'creator_name',
            'assignee', 'assignee_name', 'solution', 'reject_reason',
            'attachments', 'history', 'created_at', 'updated_at'
        ]
    
    def get_module_path(self, obj):
        if obj.module:
            return f"{obj.module.product.project.name} / {obj.module.product.name} / {obj.module.name}"
        return ''
    
    def get_module_cascade(self, obj):
        if obj.module:
            return [obj.module.product.project.id, obj.module.product.id, obj.module.id]
        return []


class BugCreateSerializer(serializers.ModelSerializer):
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
        attachments = validated_data.pop('attachments', [])
        validated_data['creator'] = self.context['request'].user
        bug = Bug.objects.create(**validated_data)
        
        for attachment in attachments:
            BugAttachment.objects.create(bug=bug, file=attachment)
        
        return bug


class BugUpdateSerializer(serializers.ModelSerializer):
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
        attachments = validated_data.pop('attachments', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        for attachment in attachments:
            BugAttachment.objects.create(bug=instance, file=attachment)
        
        return instance


class BugStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Bug.STATUS_CHOICES)
    solution = serializers.CharField(required=False, allow_blank=True)
    reject_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        status = attrs.get('status')
        if status == 'resolved' and not attrs.get('solution'):
            raise serializers.ValidationError({'solution': '解决BUG时必须填写解决说明'})
        if status == 'rejected' and not attrs.get('reject_reason'):
            raise serializers.ValidationError({'reject_reason': '驳回BUG时必须填写驳回原因'})
        return attrs

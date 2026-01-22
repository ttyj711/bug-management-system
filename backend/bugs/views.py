"""
BUG模块 - 视图层
处理BUG相关的所有HTTP请求，包括CRUD、状态流转、分配、附件管理等
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q

from .models import Bug, BugAttachment
from .serializers import (
    BugListSerializer, BugDetailSerializer, BugCreateSerializer,
    BugUpdateSerializer, BugStatusUpdateSerializer, BugAttachmentSerializer
)


class BugViewSet(viewsets.ModelViewSet):
    """
    BUG管理视图集
    
    提供BUG的完整CRUD操作和状态管理：
    
    基础接口：
    - GET /api/bugs/ - 获取BUG列表（支持多条件筛选）
    - POST /api/bugs/ - 创建BUG（测试人员、管理员可创建）
    - GET /api/bugs/{id}/ - 获取BUG详情
    - PUT/PATCH /api/bugs/{id}/ - 更新BUG信息
    - DELETE /api/bugs/{id}/ - 删除BUG（仅超管）
    
    扩展接口：
    - POST /api/bugs/{id}/update_status/ - 更新BUG状态
    - POST /api/bugs/{id}/assign/ - 分配BUG给开发人员
    - POST /api/bugs/{id}/upload_attachment/ - 上传附件
    - DELETE /api/bugs/{id}/attachment/{attachment_id}/ - 删除附件
    
    查询参数：
    - status: 按状态筛选（pending/processing/resolved/rejected/closed）
    - severity: 按严重程度筛选
    - priority: 按优先级筛选
    - assignee: 按处理人ID筛选
    - creator: 按创建人ID筛选
    - search: 按标题或描述搜索
    - my_bugs: 'created'=我创建的, 'assigned'=分配给我的
    """
    queryset = Bug.objects.all()
    # 支持文件上传和JSON数据
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        """
        根据操作类型选择序列化器
        - 列表页使用简化的序列化器提高性能
        - 详情页使用完整的序列化器
        - 创建和更新使用各自的序列化器
        """
        if self.action == 'list':
            return BugListSerializer
        elif self.action == 'retrieve':
            return BugDetailSerializer
        elif self.action == 'create':
            return BugCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BugUpdateSerializer
        return BugListSerializer
    
    def get_permissions(self):
        """所有BUG操作都需要登录"""
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        获取BUG查询集
        支持多条件筛选，并根据用户角色返回不同范围的数据
        """
        user = self.request.user
        queryset = Bug.objects.all()
        
        # 从URL参数获取筛选条件
        status_param = self.request.query_params.get('status')
        severity = self.request.query_params.get('severity')
        priority = self.request.query_params.get('priority')
        assignee = self.request.query_params.get('assignee')
        creator = self.request.query_params.get('creator')
        search = self.request.query_params.get('search')
        my_bugs = self.request.query_params.get('my_bugs')
        
        # 应用筛选条件
        if status_param:
            queryset = queryset.filter(status=status_param)
        if severity:
            queryset = queryset.filter(severity=severity)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        if creator:
            queryset = queryset.filter(creator_id=creator)
        if search:
            # 在标题和描述中搜索关键词
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 我的BUG筛选（快捷过滤器）
        if my_bugs == 'created':
            queryset = queryset.filter(creator=user)  # 我创建的
        elif my_bugs == 'assigned':
            queryset = queryset.filter(assignee=user)  # 分配给我的
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        创建BUG
        
        权限：超级管理员、普通管理员、测试人员可创建
        开发人员不能创建BUG（只能处理）
        """
        user = request.user
        if user.role not in ('super_admin', 'admin', 'tester'):
            return Response({'detail': '您没有权限提报BUG'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        更新BUG
        
        权限规则：
        - 超级管理员：可编辑所有BUG
        - 测试人员：只能编辑自己创建的且状态为"待处理"的BUG
        """
        user = request.user
        bug = self.get_object()
        
        # 超级管理员可以编辑所有BUG
        if user.is_super_admin:
            return super().update(request, *args, **kwargs)
        
        # 测试人员权限检查
        if user.is_tester:
            if bug.creator != user:
                return Response({'detail': '您只能编辑自己创建的BUG'}, status=status.HTTP_403_FORBIDDEN)
            if bug.status != 'pending':
                return Response({'detail': '只能编辑待处理状态的BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除BUG
        
        权限：仅超级管理员可删除BUG
        防止误删或恶意删除
        """
        if not request.user.is_super_admin:
            return Response({'detail': '您没有权限删除BUG'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        更新BUG状态
        
        接口：POST /api/bugs/{id}/update_status/
        
        请求参数：
        - status: 新状态
        - solution: 解决说明（状态为resolved时）
        - reject_reason: 驳回原因（状态为rejected时）
        
        权限规则：
        - 开发人员：只能处理分配给自己的BUG，可将状态改为processing/resolved/rejected
        - 超级管理员：可以修改任何BUG的状态
        """
        user = request.user
        bug = self.get_object()
        
        serializer = BugStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        
        # 开发人员权限检查
        if user.is_developer:
            # 只能处理分配给自己的BUG
            if bug.assignee != user:
                return Response({'detail': '您只能处理分配给自己的BUG'}, status=status.HTTP_403_FORBIDDEN)
            # 只能改为特定状态
            if new_status not in ('processing', 'resolved', 'rejected'):
                return Response({'detail': '您只能将状态改为处理中、已解决或已驳回'}, status=status.HTTP_403_FORBIDDEN)
        elif not user.is_super_admin:
            return Response({'detail': '您没有权限修改BUG状态'}, status=status.HTTP_403_FORBIDDEN)
        
        # 更新状态
        bug.status = new_status
        # 根据状态保存附加信息
        if new_status == 'resolved':
            bug.solution = serializer.validated_data.get('solution', '')
        elif new_status == 'rejected':
            bug.reject_reason = serializer.validated_data.get('reject_reason', '')
        bug.save()
        
        return Response({'detail': '状态更新成功', 'status': bug.status})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        分配BUG给开发人员
        
        接口：POST /api/bugs/{id}/assign/
        权限：超级管理员、普通管理员
        
        请求参数：
        - assignee: 开发人员的用户ID
        """
        user = request.user
        if not user.is_super_admin and not user.is_admin:
            return Response({'detail': '您没有权限分配BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        bug = self.get_object()
        assignee_id = request.data.get('assignee')
        
        if not assignee_id:
            return Response({'detail': '请选择处理人'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新处理人
        bug.assignee_id = assignee_id
        bug.save()
        
        return Response({'detail': '分配成功'})
    
    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        """
        上传BUG附件（截图）
        
        接口：POST /api/bugs/{id}/upload_attachment/
        请求：multipart/form-data，包含file字段
        
        返回：上传成功的附件信息
        """
        bug = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response({'detail': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建附件记录
        attachment = BugAttachment.objects.create(bug=bug, file=file)
        serializer = BugAttachmentSerializer(attachment)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='attachment/(?P<attachment_id>[^/.]+)')
    def delete_attachment(self, request, pk=None, attachment_id=None):
        """
        删除BUG附件
        
        接口：DELETE /api/bugs/{id}/attachment/{attachment_id}/
        """
        bug = self.get_object()
        
        try:
            attachment = bug.attachments.get(id=attachment_id)
            attachment.delete()
            return Response({'detail': '删除成功'})
        except BugAttachment.DoesNotExist:
            return Response({'detail': '附件不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def copy(self, request, pk=None):
        """
        复制BUG功能
        
        接口：GET /api/bugs/{id}/copy/
        功能：返回复制后的BUG数据，用于新BUG提报
        
        返回数据规则：
        - 基础信息类字段：完全复用
        - 描述类字段：完全复用，标题添加【复制】前缀
        - 关联信息类字段：完全复用
        - 状态类字段：重置
        - 附件信息：返回附件列表
        """
        original_bug = self.get_object()
        
        # 构造级联选择器的值数组
        module_cascade = []
        if original_bug.module:
            module_cascade = [original_bug.module.product.project.id, original_bug.module.product.id, original_bug.module.id]
        
        # 复制基本信息，根据规则处理各个字段
        copy_data = {
            # 基础信息类字段：完全复用
            'module': original_bug.module.id if original_bug.module else None,
            'module_cascade': module_cascade,
            'severity': original_bug.severity,
            'priority': original_bug.priority,
            
            # 描述类字段：完全复用，标题添加【复制】前缀
            'title': f'【复制】{original_bug.title}',
            'description': original_bug.description,
            
            # 关联信息类字段：完全复用
            'version': original_bug.version,
            
            # 状态类字段：重置
            'status': 'pending',  # 默认设为新建
            'creator': request.user.id,  # 报告人为当前用户
            'assignee': None,  # 处理人留空
            
            # 附件信息：获取附件列表
            'attachments': [{
                'id': attachment.id,
                'file': attachment.file.url,
                'created_at': attachment.created_at
            } for attachment in original_bug.attachments.all()]
        }
        
        return Response(copy_data, status=status.HTTP_200_OK)

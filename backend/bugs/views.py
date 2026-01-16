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
    """BUG管理视图集"""
    queryset = Bug.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
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
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Bug.objects.all()
        
        # 筛选条件
        status_param = self.request.query_params.get('status')
        severity = self.request.query_params.get('severity')
        priority = self.request.query_params.get('priority')
        assignee = self.request.query_params.get('assignee')
        creator = self.request.query_params.get('creator')
        search = self.request.query_params.get('search')
        my_bugs = self.request.query_params.get('my_bugs')
        
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
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 我的BUG筛选
        if my_bugs == 'created':
            queryset = queryset.filter(creator=user)
        elif my_bugs == 'assigned':
            queryset = queryset.filter(assignee=user)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """创建BUG - 测试人员、管理员可创建"""
        user = request.user
        if user.role not in ('super_admin', 'admin', 'tester'):
            return Response({'detail': '您没有权限提报BUG'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """更新BUG"""
        user = request.user
        bug = self.get_object()
        
        # 超级管理员可以编辑所有BUG
        if user.is_super_admin:
            return super().update(request, *args, **kwargs)
        
        # 测试人员只能编辑自己创建的且未处理的BUG
        if user.is_tester:
            if bug.creator != user:
                return Response({'detail': '您只能编辑自己创建的BUG'}, status=status.HTTP_403_FORBIDDEN)
            if bug.status != 'pending':
                return Response({'detail': '只能编辑待处理状态的BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """删除BUG - 仅超级管理员"""
        if not request.user.is_super_admin:
            return Response({'detail': '您没有权限删除BUG'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新BUG状态"""
        user = request.user
        bug = self.get_object()
        
        serializer = BugStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        
        # 权限检查
        if user.is_developer:
            # 开发人员只能处理分配给自己的BUG
            if bug.assignee != user:
                return Response({'detail': '您只能处理分配给自己的BUG'}, status=status.HTTP_403_FORBIDDEN)
            # 开发人员可以将状态改为: 处理中、已解决、已驳回
            if new_status not in ('processing', 'resolved', 'rejected'):
                return Response({'detail': '您只能将状态改为处理中、已解决或已驳回'}, status=status.HTTP_403_FORBIDDEN)
        elif not user.is_super_admin:
            return Response({'detail': '您没有权限修改BUG状态'}, status=status.HTTP_403_FORBIDDEN)
        
        bug.status = new_status
        if new_status == 'resolved':
            bug.solution = serializer.validated_data.get('solution', '')
        elif new_status == 'rejected':
            bug.reject_reason = serializer.validated_data.get('reject_reason', '')
        bug.save()
        
        return Response({'detail': '状态更新成功', 'status': bug.status})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """分配BUG给开发人员"""
        user = request.user
        if not user.is_super_admin and not user.is_admin:
            return Response({'detail': '您没有权限分配BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        bug = self.get_object()
        assignee_id = request.data.get('assignee')
        
        if not assignee_id:
            return Response({'detail': '请选择处理人'}, status=status.HTTP_400_BAD_REQUEST)
        
        bug.assignee_id = assignee_id
        bug.save()
        
        return Response({'detail': '分配成功'})
    
    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        """上传BUG附件"""
        bug = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response({'detail': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        attachment = BugAttachment.objects.create(bug=bug, file=file)
        serializer = BugAttachmentSerializer(attachment)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='attachment/(?P<attachment_id>[^/.]+)')
    def delete_attachment(self, request, pk=None, attachment_id=None):
        """删除BUG附件"""
        bug = self.get_object()
        
        try:
            attachment = bug.attachments.get(id=attachment_id)
            attachment.delete()
            return Response({'detail': '删除成功'})
        except BugAttachment.DoesNotExist:
            return Response({'detail': '附件不存在'}, status=status.HTTP_404_NOT_FOUND)

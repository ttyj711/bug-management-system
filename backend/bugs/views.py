"""
BUG模块 - 视图层
处理BUG相关的所有HTTP请求，包括CRUD、状态流转、分配、附件管理等
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q

from .models import Bug, BugAttachment, BugHistory
from .serializers import (
    BugListSerializer, BugDetailSerializer, BugCreateSerializer,
    BugUpdateSerializer, BugStatusUpdateSerializer, BugAttachmentSerializer
)


def record_history(bug, user, action, field_name='', old_value='', new_value='', description=''):
    BugHistory.objects.create(
        bug=bug,
        operator=user,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        description=description
    )


def send_notification(user, notification_type, title, content, bug_id=None):
    from notifications.models import Notification
    Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        content=content,
        bug_id=bug_id
    )


class BugViewSet(viewsets.ModelViewSet):
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
        
        # 数据权限控制
        if user.is_super_admin or user.is_admin:
            pass
        elif user.is_tester:
            queryset = queryset.filter(Q(creator=user) | Q(assignee=user))
        elif user.is_developer:
            queryset = queryset.filter(assignee=user)
        else:
            queryset = queryset.none()
        
        status_param = self.request.query_params.get('status')
        severity = self.request.query_params.get('severity')
        priority = self.request.query_params.get('priority')
        assignee = self.request.query_params.get('assignee')
        creator = self.request.query_params.get('creator')
        search = self.request.query_params.get('search')
        my_bugs = self.request.query_params.get('my_bugs')
        module = self.request.query_params.get('module')
        date_start = self.request.query_params.get('date_start')
        date_end = self.request.query_params.get('date_end')
        
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
        if module:
            queryset = queryset.filter(module_id=module)
        if date_start:
            queryset = queryset.filter(created_at__date__gte=date_start)
        if date_end:
            queryset = queryset.filter(created_at__date__lte=date_end)
        
        if my_bugs == 'created':
            queryset = queryset.filter(creator=user)
        elif my_bugs == 'assigned':
            queryset = queryset.filter(assignee=user)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role not in ('super_admin', 'admin', 'tester'):
            return Response({'detail': '您没有权限提报BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        response = super().create(request, *args, **kwargs)
        
        bug = Bug.objects.get(id=response.data['id'])
        record_history(bug, user, 'create', description=f'创建了BUG: {bug.title}')
        
        return response
    
    def update(self, request, *args, **kwargs):
        user = request.user
        bug = self.get_object()
        
        if user.is_super_admin:
            pass
        elif user.is_tester:
            if bug.creator != user:
                return Response({'detail': '您只能编辑自己创建的BUG'}, status=status.HTTP_403_FORBIDDEN)
            if bug.status != 'pending':
                return Response({'detail': '只能编辑待处理状态的BUG'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': '您没有权限编辑BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        old_values = {
            'title': bug.title,
            'description': bug.description[:100] if bug.description else '',
            'severity': bug.get_severity_display(),
            'priority': bug.get_priority_display(),
            'version': bug.version,
            'assignee': bug.assignee.username if bug.assignee else '',
        }
        
        response = super().update(request, *args, **kwargs)
        
        bug.refresh_from_db()
        new_values = {
            'title': bug.title,
            'description': bug.description[:100] if bug.description else '',
            'severity': bug.get_severity_display(),
            'priority': bug.get_priority_display(),
            'version': bug.version,
            'assignee': bug.assignee.username if bug.assignee else '',
        }
        
        for field, old_val in old_values.items():
            new_val = new_values[field]
            if old_val != new_val:
                record_history(
                    bug, user, 'update',
                    field_name=field,
                    old_value=str(old_val),
                    new_value=str(new_val),
                    description=f'将{field}从"{old_val}"修改为"{new_val}"'
                )
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_super_admin:
            return Response({'detail': '您没有权限删除BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        bug = self.get_object()
        record_history(bug, request.user, 'delete', description=f'删除了BUG: {bug.title}')
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        user = request.user
        bug = self.get_object()
        
        serializer = BugStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        
        if user.is_developer:
            if bug.assignee != user:
                return Response({'detail': '您只能处理分配给自己的BUG'}, status=status.HTTP_403_FORBIDDEN)
            if new_status not in ('processing', 'resolved', 'rejected'):
                return Response({'detail': '您只能将状态改为处理中、已解决或已驳回'}, status=status.HTTP_403_FORBIDDEN)
        elif not user.is_super_admin:
            return Response({'detail': '您没有权限修改BUG状态'}, status=status.HTTP_403_FORBIDDEN)
        
        old_status = bug.get_status_display()
        
        bug.status = new_status
        if new_status == 'resolved':
            bug.solution = serializer.validated_data.get('solution', '')
        elif new_status == 'rejected':
            bug.reject_reason = serializer.validated_data.get('reject_reason', '')
        bug.save()
        
        new_status_display = bug.get_status_display()
        record_history(
            bug, user, 'status_change',
            field_name='status',
            old_value=old_status,
            new_value=new_status_display,
            description=f'将状态从"{old_status}"改为"{new_status_display}"'
        )
        
        if bug.creator and bug.creator != user:
            send_notification(
                bug.creator,
                'bug_status',
                f'BUG状态变更: {bug.title}',
                f'您的BUG "#{bug.id} {bug.title}" 状态已从"{old_status}"变更为"{new_status_display}"',
                bug.id
            )
        
        return Response({'detail': '状态更新成功', 'status': bug.status})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        user = request.user
        if not user.is_super_admin and not user.is_admin:
            return Response({'detail': '您没有权限分配BUG'}, status=status.HTTP_403_FORBIDDEN)
        
        bug = self.get_object()
        assignee_id = request.data.get('assignee')
        
        if not assignee_id:
            return Response({'detail': '请选择处理人'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_assignee = bug.assignee.username if bug.assignee else '未分配'
        
        bug.assignee_id = assignee_id
        bug.save()
        
        new_assignee = bug.assignee.username if bug.assignee else '未分配'
        record_history(
            bug, user, 'assign',
            field_name='assignee',
            old_value=old_assignee,
            new_value=new_assignee,
            description=f'将处理人从"{old_assignee}"改为"{new_assignee}"'
        )
        
        if bug.assignee and bug.assignee != user:
            send_notification(
                bug.assignee,
                'bug_assigned',
                f'新BUG分配: {bug.title}',
                f'您被分配了一个新的BUG "#{bug.id} {bug.title}"，请及时处理',
                bug.id
            )
        
        return Response({'detail': '分配成功'})
    
    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        bug = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response({'detail': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        attachment = BugAttachment.objects.create(bug=bug, file=file)
        serializer = BugAttachmentSerializer(attachment)
        
        record_history(
            bug, request.user, 'update',
            field_name='attachment',
            new_value=file.name,
            description=f'上传了附件: {file.name}'
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='attachment/(?P<attachment_id>[^/.]+)')
    def delete_attachment(self, request, pk=None, attachment_id=None):
        bug = self.get_object()
        
        try:
            attachment = bug.attachments.get(id=attachment_id)
            file_name = attachment.file.name
            attachment.delete()
            
            record_history(
                bug, request.user, 'update',
                field_name='attachment',
                old_value=file_name,
                description=f'删除了附件: {file_name}'
            )
            
            return Response({'detail': '删除成功'})
        except BugAttachment.DoesNotExist:
            return Response({'detail': '附件不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        user = request.user
        
        if user.is_super_admin or user.is_admin:
            queryset = Bug.objects.all()
        elif user.is_tester:
            queryset = Bug.objects.filter(Q(creator=user) | Q(assignee=user))
        elif user.is_developer:
            queryset = Bug.objects.filter(assignee=user)
        else:
            queryset = Bug.objects.none()
        
        total = queryset.count()
        
        status_data = {
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'rejected': queryset.filter(status='rejected').count(),
            'closed': queryset.filter(status='closed').count(),
        }
        
        severity_data = {
            'critical': queryset.filter(severity='critical').count(),
            'major': queryset.filter(severity='major').count(),
            'minor': queryset.filter(severity='minor').count(),
            'trivial': queryset.filter(severity='trivial').count(),
        }
        
        priority_data = {
            'urgent': queryset.filter(priority='urgent').count(),
            'high': queryset.filter(priority='high').count(),
            'medium': queryset.filter(priority='medium').count(),
            'low': queryset.filter(priority='low').count(),
        }
        
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        trend_data = []
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            created = queryset.filter(created_at__date=date).count()
            resolved = queryset.filter(
                status='resolved',
                updated_at__date=date
            ).count()
            trend_data.append({
                'date': date.strftime('%m-%d'),
                'created': created,
                'resolved': resolved
            })
        
        module_stats = queryset.filter(
            module__isnull=False
        ).values(
            'module__name',
            'module__product__name',
            'module__product__project__name'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        
        module_data = [
            {
                'name': f"{item['module__product__project__name']}/{item['module__product__name']}/{item['module__name']}",
                'count': item['count']
            }
            for item in module_stats
        ]
        
        developer_stats = queryset.filter(
            assignee__isnull=False,
            status__in=['pending', 'processing']
        ).values(
            'assignee__username'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        
        developer_data = [
            {'name': item['assignee__username'], 'count': item['count']}
            for item in developer_stats
        ]
        
        return Response({
            'total': total,
            'status': status_data,
            'severity': severity_data,
            'priority': priority_data,
            'trend': trend_data,
            'module': module_data,
            'developer': developer_data
        })

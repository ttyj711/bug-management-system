from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    消息通知视图集
    
    提供消息通知的查询和标记已读功能
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读消息数量"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有消息为已读"""
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({'detail': '已标记所有消息为已读'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记单条消息为已读"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'detail': '已标记为已读'})

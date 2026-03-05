"""
消息通知模型
记录用户的通知消息
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    消息通知模型
    
    记录系统发送给用户的通知消息
    """
    
    TYPE_CHOICES = (
        ('bug_assigned', 'BUG分配'),
        ('bug_status', '状态变更'),
        ('bug_comment', '评论回复'),
        ('system', '系统通知'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )
    type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES)
    title = models.CharField('通知标题', max_length=200)
    content = models.TextField('通知内容')
    bug_id = models.IntegerField('关联BUG ID', null=True, blank=True)
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = '消息通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.title}'

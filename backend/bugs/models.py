from django.db import models
from django.conf import settings


class Bug(models.Model):
    """BUG模型"""
    
    SEVERITY_CHOICES = (
        ('critical', '致命'),
        ('major', '严重'),
        ('minor', '一般'),
        ('trivial', '轻微'),
    )
    
    PRIORITY_CHOICES = (
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    )
    
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('rejected', '已驳回'),
        ('closed', '已关闭'),
    )
    
    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述')
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES, default='minor')
    priority = models.CharField('优先级', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 关联到模块（项目-产品-模块级联）
    module = models.ForeignKey(
        'modules.Module',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bugs',
        verbose_name='所属模块'
    )
    version = models.CharField('版本号', max_length=50, blank=True, default='')
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_bugs',
        verbose_name='创建人'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_bugs',
        verbose_name='处理人'
    )
    
    solution = models.TextField('解决说明', blank=True, default='')
    reject_reason = models.TextField('驳回原因', blank=True, default='')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'bugs'
        verbose_name = 'BUG'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BugAttachment(models.Model):
    """BUG附件（截图）"""
    
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='attachments', verbose_name='BUG')
    file = models.ImageField('附件', upload_to='bug_attachments/%Y/%m/')
    created_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        db_table = 'bug_attachments'
        verbose_name = 'BUG附件'
        verbose_name_plural = verbose_name

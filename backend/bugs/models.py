"""
BUG模块 - 数据模型
定义BUG及其附件的数据结构
"""
from django.db import models
from django.conf import settings


class Bug(models.Model):
    """
    BUG模型
    
    记录系统中发现的缺陷信息，包括：
    - 基本信息：标题、描述、版本号
    - 分类信息：严重程度、优先级、所属模块
    - 状态流转：待处理 -> 处理中 -> 已解决/已驳回 -> 已关闭
    - 人员关联：创建人（测试）、处理人（开发）
    - 处理结果：解决说明或驳回原因
    
    状态流转说明：
    - pending(待处理): BUG初始状态，等待分配处理人
    - processing(处理中): 开发人员正在处理
    - resolved(已解决): 开发人员已修复，等待测试验证
    - rejected(已驳回): 非BUG或无法复现，需说明驳回原因
    - closed(已关闭): BUG处理完成，测试验证通过
    """
    
    # 严重程度选项（影响系统的程度）
    SEVERITY_CHOICES = (
        ('critical', '致命'),  # 系统崩溃、数据丢失等严重问题
        ('major', '严重'),     # 主要功能不可用
        ('minor', '一般'),     # 功能异常但有替代方案
        ('trivial', '轻微'),   # 界面问题、文案错误等
    )
    
    # 优先级选项（处理的紧急程度）
    PRIORITY_CHOICES = (
        ('high', '高'),    # 需要立即处理
        ('medium', '中'),  # 正常排期处理
        ('low', '低'),     # 有空再处理
    )
    
    # 状态选项（BUG处理流程）
    STATUS_CHOICES = (
        ('pending', '待处理'),     # 新建状态，等待分配
        ('processing', '处理中'),  # 开发处理中
        ('resolved', '已解决'),    # 开发已修复
        ('rejected', '已驳回'),    # 非BUG或无法复现
        ('closed', '已关闭'),      # 验证通过，关闭
    )
    
    # BUG标题
    title = models.CharField('标题', max_length=200)
    # BUG详细描述（复现步骤、期望结果、实际结果等）
    description = models.TextField('描述')
    # 严重程度
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES, default='minor')
    # 优先级
    priority = models.CharField('优先级', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    # 当前状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 关联到模块（项目-产品-模块级联结构）
    # 通过此字段可追溯BUG属于哪个项目的哪个产品的哪个功能模块
    module = models.ForeignKey(
        'modules.Module',
        on_delete=models.SET_NULL,  # 模块删除时，BUG的模块字段置空
        null=True,
        blank=True,
        related_name='bugs',  # 反向查询：module.bugs.all()
        verbose_name='所属模块'
    )
    # 发现BUG的软件版本号
    version = models.CharField('版本号', max_length=50, blank=True, default='')
    
    # BUG创建人（通常是测试人员）
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,  # 用户删除时，其创建的BUG也删除
        related_name='created_bugs',  # 反向查询：user.created_bugs.all()
        verbose_name='创建人'
    )
    # BUG处理人（通常是开发人员）
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  # 用户删除时，处理人字段置空
        null=True, 
        blank=True,
        related_name='assigned_bugs',  # 反向查询：user.assigned_bugs.all()
        verbose_name='处理人'
    )
    
    # 解决说明（开发人员填写修复方案）
    solution = models.TextField('解决说明', blank=True, default='')
    # 驳回原因（如果BUG被驳回，需说明原因）
    reject_reason = models.TextField('驳回原因', blank=True, default='')
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'bugs'  # 数据库表名
        verbose_name = 'BUG'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']  # 按创建时间倒序，最新的在前

    def __str__(self):
        """返回BUG标题作为字符串表示"""
        return self.title


class BugAttachment(models.Model):
    """
    BUG附件模型
    
    存储BUG相关的截图或文件，用于辅助描述和复现BUG
    支持上传图片类型的附件，按年月分目录存储
    """
    
    # 关联的BUG
    bug = models.ForeignKey(
        Bug, 
        on_delete=models.CASCADE,  # BUG删除时，附件也删除
        related_name='attachments',  # 反向查询：bug.attachments.all()
        verbose_name='BUG'
    )
    # 附件文件（图片），按年月分目录存储
    file = models.ImageField('附件', upload_to='bug_attachments/%Y/%m/')
    # 上传时间
    created_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        db_table = 'bug_attachments'  # 数据库表名
        verbose_name = 'BUG附件'
        verbose_name_plural = verbose_name

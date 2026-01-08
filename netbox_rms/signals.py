"""
NetBox RMS 信号处理器

实现业务逻辑的自动化处理
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import TaskDetail, ResourceLedger
from .choices import TaskTypeChoices, ChangeTypeChoices


# 所有信号处理器已被移除，因为相关字段已不存在
# 如需添加新的业务逻辑，请在此处定义信号处理器

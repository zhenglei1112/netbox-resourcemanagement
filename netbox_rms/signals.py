"""
NetBox RMS 信号处理器

实现业务逻辑的自动化处理
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import TaskDetail, ResourceLedger
from .choices import TaskTypeChoices, LifecycleStatusChoices, ChangeTypeChoices


@receiver(post_save, sender=TaskDetail)
def handle_task_status_change(sender, instance: TaskDetail, created: bool, **kwargs):
    """
    处理任务状态变更时的业务逻辑
    
    - 当变更单确认业务撤销时，自动将关联资源标记为终止
    """
    if instance.task_type != TaskTypeChoices.CHANGE:
        return
    
    # 检查是否是业务撤销变更
    if ChangeTypeChoices.TOGGLE not in instance.change_types:
        return
    
    # 检查变更后状态是否包含"取消"关键字
    if not instance.new_value:
        return
    
    cancel_keywords = ['取消', '撤销', '拆机', '终止', '关闭']
    is_cancellation = any(kw in instance.new_value for kw in cancel_keywords)
    
    if not is_cancellation:
        return
    
    # 查找关联资源并更新状态
    if instance.lifecycle_status == LifecycleStatusChoices.TERMINATED:
        # 更新来源工单下的所有资源
        ResourceLedger.objects.filter(
            service_order=instance.service_order
        ).update(
            lifecycle_status=LifecycleStatusChoices.TERMINATED
        )


@receiver(pre_save, sender=TaskDetail)
def auto_fill_change_order_values(sender, instance: TaskDetail, **kwargs):
    """
    变更单自动填充原值
    
    - 从原工单的任务中拉取 A/Z 端、带宽等信息
    """
    if instance.pk:  # 只在创建时执行
        return
    
    if instance.task_type != TaskTypeChoices.CHANGE:
        return
    
    parent_order = instance.service_order.parent_order
    if not parent_order:
        return
    
    # 查找原工单的第一个任务（通常是调配任务）
    original_task = parent_order.tasks.first()
    if not original_task:
        return
    
    # 自动填充原值字段
    if not instance.old_value:
        old_values = []
        if original_task.site_a:
            old_values.append(f"原A端：{original_task.site_a}")
        if original_task.site_z:
            old_values.append(f"原Z端：{original_task.site_z}")
        if original_task.bandwidth:
            old_values.append(f"原带宽：{original_task.bandwidth}")
        if original_task.circuit_id:
            old_values.append(f"原电路：{original_task.circuit_id}")
        
        instance.old_value = '\n'.join(old_values)
    
    # 复制技术参数作为参考
    if not instance.site_a:
        instance.site_a = original_task.site_a
    if not instance.site_z:
        instance.site_z = original_task.site_z
    if not instance.bandwidth:
        instance.bandwidth = original_task.bandwidth
    if not instance.circuit_id:
        instance.circuit_id = original_task.circuit_id

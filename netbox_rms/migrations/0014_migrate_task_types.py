# Generated migration for task type consolidation

from django.db import migrations


def migrate_task_types_forward(apps, schema_editor):
    """
    将旧的任务类型迁移到新的三种类型：
    - verification (资源核查) → activation (入网/开通)
    - allocation (资源调配) → activation (入网/开通)
    - hosting (设备托管) → activation (入网/开通)
    - change (资源变更) → change (变更) [保持不变]
    """
    TaskDetail = apps.get_model('netbox_rms', 'TaskDetail')
    
    # 映射规则
    migration_map = {
        'verification': 'activation',
        'allocation': 'activation',
        'hosting': 'activation',
    }
    
    # 执行迁移
    for old_type, new_type in migration_map.items():
        TaskDetail.objects.filter(task_type=old_type).update(task_type=new_type)


def migrate_task_types_backward(apps, schema_editor):
    """
    回滚迁移（将 activation 恢复为 allocation）
    注意：无法完全恢复原始数据，只能设置为一个默认值
    """
    TaskDetail = apps.get_model('netbox_rms', 'TaskDetail')
    
    # 将所有 activation 和 deactivation 都恢复为 allocation
    TaskDetail.objects.filter(task_type='activation').update(task_type='allocation')
    TaskDetail.objects.filter(task_type='deactivation').update(task_type='allocation')


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_rms', '0013_taskdetail_assignee'),
    ]

    operations = [
        migrations.RunPython(
            migrate_task_types_forward,
            reverse_code=migrate_task_types_backward,
        ),
    ]

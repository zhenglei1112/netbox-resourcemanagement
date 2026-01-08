# Generated migration for removing lifecycle_status field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_rms', '0014_migrate_task_types'),
    ]

    operations = [
        # 删除 TaskDetail 的 lifecycle_status 字段
        migrations.RemoveField(
            model_name='taskdetail',
            name='lifecycle_status',
        ),
        # 删除 ResourceLedger 的 lifecycle_status 字段
        migrations.RemoveField(
            model_name='resourceledger',
            name='lifecycle_status',
        ),
    ]

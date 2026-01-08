# Generated migration for adding execution_department field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_rms', '0016_merge_20260107_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskdetail',
            name='execution_department',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pipeline', '管线部'),
                    ('operation', '运维部')
                ],
                help_text='负责执行此任务的部门',
                max_length=50,
                verbose_name='执行部门'
            ),
        ),
    ]

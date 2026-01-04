"""
NetBox RMS 表格定义

使用 django-tables2 定义列表页面的表格
"""
import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from .models import ServiceOrder, TaskDetail, ResourceLedger


class ServiceOrderTable(NetBoxTable):
    """业务主工单表格"""
    
    order_no = tables.Column(
        linkify=True,
        verbose_name=_('业务单号'),
    )
    
    customer_name = tables.Column(
        verbose_name=_('客户单位'),
    )
    
    project_code = tables.Column(
        verbose_name=_('项目编号'),
    )
    
    sales_contact = tables.Column(
        verbose_name=_('销售负责人'),
    )
    
    apply_date = tables.DateColumn(
        verbose_name=_('申请时间'),
    )
    
    deadline_date = tables.DateColumn(
        verbose_name=_('完成期限'),
    )
    
    billing_start_date = tables.DateColumn(
        verbose_name=_('计费日期'),
    )
    
    parent_order = tables.Column(
        linkify=True,
        verbose_name=_('原单号'),
    )
    
    task_count = tables.Column(
        accessor='tasks__count',
        verbose_name=_('任务数'),
        orderable=False,
    )
    
    class Meta(NetBoxTable.Meta):
        model = ServiceOrder
        fields = (
            'pk', 'id', 'order_no', 'customer_name', 'project_code',
            'sales_contact', 'apply_date', 'deadline_date',
            'billing_start_date', 'parent_order', 'task_count', 'actions',
        )
        default_columns = (
            'order_no', 'customer_name', 'project_code', 'apply_date',
            'deadline_date', 'task_count', 'actions',
        )


class TaskDetailTable(NetBoxTable):
    """执行任务详情表格"""
    
    service_order = tables.Column(
        linkify=True,
        verbose_name=_('主工单'),
    )
    
    task_type = columns.ChoiceFieldColumn(
        verbose_name=_('任务类型'),
    )
    
    lifecycle_status = columns.ChoiceFieldColumn(
        verbose_name=_('生命周期'),
    )
    
    execution_status = columns.ChoiceFieldColumn(
        verbose_name=_('执行状态'),
    )
    
    site_a = tables.Column(
        verbose_name=_('A端站点'),
    )
    
    site_z = tables.Column(
        verbose_name=_('Z端站点'),
    )
    
    circuit_id = tables.Column(
        verbose_name=_('电路编号'),
    )
    
    config_status = columns.BooleanColumn(
        verbose_name=_('已配置'),
    )
    
    test_status = columns.BooleanColumn(
        verbose_name=_('已测试'),
    )
    
    class Meta(NetBoxTable.Meta):
        model = TaskDetail
        fields = (
            'pk', 'id', 'service_order', 'task_type', 'lifecycle_status',
            'execution_status', 'site_a', 'site_z', 'circuit_id',
            'config_status', 'test_status', 'actions',
        )
        default_columns = (
            'service_order', 'task_type', 'lifecycle_status',
            'execution_status', 'site_a', 'site_z', 'actions',
        )


class ResourceLedgerTable(NetBoxTable):
    """资源台账表格"""
    
    resource_id = tables.Column(
        linkify=True,
        verbose_name=_('资源标识'),
    )
    
    resource_type = columns.ChoiceFieldColumn(
        verbose_name=_('资源类型'),
    )
    
    resource_name = tables.Column(
        verbose_name=_('资源名称'),
    )
    
    service_order = tables.Column(
        linkify=True,
        verbose_name=_('来源工单'),
    )
    
    lifecycle_status = columns.ChoiceFieldColumn(
        verbose_name=_('状态'),
    )
    
    class Meta(NetBoxTable.Meta):
        model = ResourceLedger
        fields = (
            'pk', 'id', 'resource_id', 'resource_type', 'resource_name',
            'service_order', 'lifecycle_status', 'actions',
        )
        default_columns = (
            'resource_id', 'resource_type', 'resource_name',
            'lifecycle_status', 'actions',
        )

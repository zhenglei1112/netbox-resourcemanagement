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
    
    tenant = tables.Column(
        linkify=True,
        verbose_name=_('客户单位'),
    )
    
    project_code = tables.Column(
        verbose_name=_('项目编号'),
    )
    
    sales_contact = tables.Column(
        verbose_name=_('销售负责人'),
    )
    
    business_manager = tables.Column(
        verbose_name=_('商务负责人'),
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
            'pk', 'id', 'order_no', 'tenant', 'project_code',
            'sales_contact', 'business_manager', 'apply_date', 'deadline_date',
            'billing_start_date', 'parent_order', 'task_count', 'actions',
        )
        default_columns = (
            'order_no', 'tenant', 'project_code', 'apply_date',
            'deadline_date', 'task_count', 'actions',
        )


class TaskDetailTable(NetBoxTable):
    """执行任务详情表格"""
    
    service_order = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        verbose_name=_('主工单'),
    )
    
    task_type = columns.ChoiceFieldColumn(
        verbose_name=_('任务类型'),
    )
    
    execution_status = columns.ChoiceFieldColumn(
        verbose_name=_('执行状态'),
    )
    
    execution_department = columns.ChoiceFieldColumn(
        verbose_name=_('执行部门'),
    )
    
    assignee = tables.Column(
        verbose_name=_('执行人'),
    )
    
    def render_task_type(self, value, record):
        """自定义任务类型渲染，使用模型的颜色方法"""
        from django.utils.html import format_html
        color = record.get_task_type_color()
        display = record.get_task_type_display()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            display
        )
    
    def render_execution_status(self, value, record):
        """自定义执行状态渲染，使用模型的颜色方法"""
        from django.utils.html import format_html
        color = record.get_execution_status_color()
        display = record.get_execution_status_display()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            display
        )
    
    def render_execution_department(self, value, record):
        """自定义执行部门渲染，使用模型的颜色方法"""
        from django.utils.html import format_html
        if not value:
            return self.default
        color = record.get_execution_department_color()
        display = record.get_execution_department_display()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            display
        )

    class Meta(NetBoxTable.Meta):
        model = TaskDetail
        fields = (
            'pk', 'id', 'service_order', 'task_type',
            'execution_status', 'execution_department', 'assignee', 'actions',
        )
        default_columns = (
            'service_order', 'task_type',
            'execution_status', 'execution_department', 'assignee', 'actions',
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
    
    class Meta(NetBoxTable.Meta):
        model = ResourceLedger
        fields = (
            'pk', 'id', 'resource_id', 'resource_type', 'resource_name',
            'service_order', 'actions',
        )
        default_columns = (
            'resource_id', 'resource_type', 'resource_name',
            'actions',
        )

"""
NetBox RMS 表单定义

用于创建和编辑数据的 Django 表单
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, CommentField
from utilities.forms.rendering import FieldSet

from .models import ServiceOrder, TaskDetail, ResourceLedger
from .choices import (
    TaskTypeChoices,
    LifecycleStatusChoices,
    ExecutionStatusChoices,
    ResourceTypeChoices,
)


# =============================================================================
# ServiceOrder 表单
# =============================================================================

class ServiceOrderForm(NetBoxModelForm):
    """业务主工单表单"""
    
    parent_order = DynamicModelChoiceField(
        queryset=ServiceOrder.objects.all(),
        required=False,
        label=_('关联原单号'),
        help_text=_('变更单必须关联原调配单'),
    )
    
    comments = CommentField()
    
    fieldsets = (
        FieldSet(
            'order_no', 'customer_name', 'project_code', 'sales_contact',
            name=_('基础信息'),
        ),
        FieldSet(
            'apply_date', 'deadline_date', 'billing_start_date',
            name=_('时间信息'),
        ),
        FieldSet(
            'parent_order',
            name=_('关联信息'),
        ),
    )
    
    class Meta:
        model = ServiceOrder
        fields = [
            'order_no', 'customer_name', 'project_code', 'sales_contact',
            'apply_date', 'deadline_date', 'billing_start_date',
            'parent_order', 'comments', 'tags',
        ]
        widgets = {
            'apply_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline_date': forms.DateInput(attrs={'type': 'date'}),
            'billing_start_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ServiceOrderFilterForm(NetBoxModelFilterSetForm):
    """业务主工单过滤表单"""
    
    model = ServiceOrder
    
    order_no = forms.CharField(
        required=False,
        label=_('业务单号'),
    )
    
    customer_name = forms.CharField(
        required=False,
        label=_('客户名称'),
    )
    
    project_code = forms.CharField(
        required=False,
        label=_('项目编号'),
    )


# =============================================================================
# TaskDetail 表单
# =============================================================================

class TaskDetailForm(NetBoxModelForm):
    """执行任务详情表单"""
    
    service_order = DynamicModelChoiceField(
        queryset=ServiceOrder.objects.all(),
        label=_('所属主工单'),
    )
    
    comments = CommentField()
    
    fieldsets = (
        FieldSet(
            'service_order', 'task_type', 'lifecycle_status', 'execution_status',
            name=_('基础信息'),
        ),
        FieldSet(
            'service_type', 'bandwidth', 'protection', 'protection_type',
            'interface_type', 'site_a', 'site_z',
            name=_('技术参数'),
        ),
        FieldSet(
            'circuit_id', 'dev_model_a', 'slot_a', 'port_a',
            'dev_model_z', 'slot_z', 'port_z',
            'config_status', 'test_status',
            name=_('运维实施参数'),
        ),
        FieldSet(
            'cable_core', 'odf_pos', 'jump_status',
            'ext_resource', 'ext_contract',
            name=_('管线实施参数'),
        ),
        FieldSet(
            'device_brand', 'dimensions', 'power_rating',
            'rack_u_pos', 'power_status',
            name=_('设备托管参数'),
        ),
        FieldSet(
            'change_types', 'old_value', 'new_value', 'ext_handle',
            name=_('变更管理参数'),
        ),
    )
    
    class Meta:
        model = TaskDetail
        fields = [
            # 基础
            'service_order', 'task_type', 'lifecycle_status', 'execution_status',
            # 技术参数
            'service_type', 'bandwidth', 'protection', 'protection_type',
            'interface_type', 'site_a', 'site_z',
            # 运维参数
            'circuit_id', 'dev_model_a', 'slot_a', 'port_a',
            'dev_model_z', 'slot_z', 'port_z', 'config_status', 'test_status',
            # 管线参数
            'cable_core', 'odf_pos', 'jump_status', 'ext_resource', 'ext_contract',
            # 托管参数
            'device_brand', 'dimensions', 'power_rating', 'rack_u_pos', 'power_status',
            # 变更参数
            'change_types', 'old_value', 'new_value', 'ext_handle',
            # 其他
            'comments', 'tags',
        ]


class TaskDetailFilterForm(NetBoxModelFilterSetForm):
    """执行任务详情过滤表单"""
    
    model = TaskDetail
    
    task_type = forms.MultipleChoiceField(
        choices=TaskTypeChoices,
        required=False,
        label=_('任务类型'),
    )
    
    lifecycle_status = forms.MultipleChoiceField(
        choices=LifecycleStatusChoices,
        required=False,
        label=_('生命周期状态'),
    )
    
    execution_status = forms.MultipleChoiceField(
        choices=ExecutionStatusChoices,
        required=False,
        label=_('执行状态'),
    )
    
    site_a = forms.CharField(
        required=False,
        label=_('A端站点'),
    )
    
    site_z = forms.CharField(
        required=False,
        label=_('Z端站点'),
    )


# =============================================================================
# ResourceLedger 表单
# =============================================================================

class ResourceLedgerForm(NetBoxModelForm):
    """资源台账表单"""
    
    service_order = DynamicModelChoiceField(
        queryset=ServiceOrder.objects.all(),
        label=_('来源工单'),
    )
    
    comments = CommentField()
    
    fieldsets = (
        FieldSet(
            'service_order', 'resource_type', 'resource_id', 'resource_name',
            name=_('资源信息'),
        ),
        FieldSet(
            'lifecycle_status',
            name=_('状态'),
        ),
        FieldSet(
            'snapshot',
            name=_('快照数据'),
        ),
    )
    
    class Meta:
        model = ResourceLedger
        fields = [
            'service_order', 'resource_type', 'resource_id', 'resource_name',
            'lifecycle_status', 'snapshot', 'comments', 'tags',
        ]
        widgets = {
            'snapshot': forms.Textarea(attrs={'rows': 5}),
        }


class ResourceLedgerFilterForm(NetBoxModelFilterSetForm):
    """资源台账过滤表单"""
    
    model = ResourceLedger
    
    resource_type = forms.MultipleChoiceField(
        choices=ResourceTypeChoices,
        required=False,
        label=_('资源类型'),
    )
    
    lifecycle_status = forms.MultipleChoiceField(
        choices=LifecycleStatusChoices,
        required=False,
        label=_('生命周期状态'),
    )
    
    resource_id = forms.CharField(
        required=False,
        label=_('资源标识'),
    )

"""
NetBox RMS 过滤器集定义

用于 REST API 和列表页面的过滤功能
"""
import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet

from .models import ServiceOrder, TaskDetail, ResourceLedger
from .choices import (
    TaskTypeChoices,
    LifecycleStatusChoices,
    ExecutionStatusChoices,
    ResourceTypeChoices,
)


class ServiceOrderFilterSet(NetBoxModelFilterSet):
    """业务主工单过滤器集"""
    
    q = django_filters.CharFilter(
        method='search',
        label=_('搜索'),
    )
    
    order_no = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('业务单号'),
    )
    
    customer_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('客户名称'),
    )
    
    project_code = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('项目编号'),
    )
    
    sales_contact = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('销售负责人'),
    )
    
    apply_date_after = django_filters.DateFilter(
        field_name='apply_date',
        lookup_expr='gte',
        label=_('申请日期起'),
    )
    
    apply_date_before = django_filters.DateFilter(
        field_name='apply_date',
        lookup_expr='lte',
        label=_('申请日期止'),
    )
    
    has_parent = django_filters.BooleanFilter(
        method='filter_has_parent',
        label=_('有原单号'),
    )
    
    class Meta:
        model = ServiceOrder
        fields = ['id', 'order_no', 'customer_name', 'project_code', 'sales_contact']
    
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(order_no__icontains=value) |
            Q(customer_name__icontains=value) |
            Q(project_code__icontains=value) |
            Q(sales_contact__icontains=value)
        )
    
    def filter_has_parent(self, queryset, name, value):
        if value:
            return queryset.filter(parent_order__isnull=False)
        return queryset.filter(parent_order__isnull=True)


class TaskDetailFilterSet(NetBoxModelFilterSet):
    """执行任务详情过滤器集"""
    
    q = django_filters.CharFilter(
        method='search',
        label=_('搜索'),
    )
    
    service_order_id = django_filters.ModelChoiceFilter(
        queryset=ServiceOrder.objects.all(),
        label=_('主工单'),
    )
    
    task_type = django_filters.MultipleChoiceFilter(
        choices=TaskTypeChoices,
        label=_('任务类型'),
    )
    
    lifecycle_status = django_filters.MultipleChoiceFilter(
        choices=LifecycleStatusChoices,
        label=_('生命周期状态'),
    )
    
    execution_status = django_filters.MultipleChoiceFilter(
        choices=ExecutionStatusChoices,
        label=_('执行状态'),
    )
    
    site_a = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('A端站点'),
    )
    
    site_z = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('Z端站点'),
    )
    
    circuit_id = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('电路编号'),
    )
    
    ext_resource = django_filters.BooleanFilter(
        label=_('外购资源'),
    )
    
    class Meta:
        model = TaskDetail
        fields = [
            'id', 'service_order', 'task_type', 'lifecycle_status',
            'execution_status', 'site_a', 'site_z', 'circuit_id',
        ]
    
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(service_order__order_no__icontains=value) |
            Q(site_a__icontains=value) |
            Q(site_z__icontains=value) |
            Q(circuit_id__icontains=value)
        )


class ResourceLedgerFilterSet(NetBoxModelFilterSet):
    """资源台账过滤器集"""
    
    q = django_filters.CharFilter(
        method='search',
        label=_('搜索'),
    )
    
    resource_type = django_filters.MultipleChoiceFilter(
        choices=ResourceTypeChoices,
        label=_('资源类型'),
    )
    
    resource_id = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('资源标识'),
    )
    
    lifecycle_status = django_filters.MultipleChoiceFilter(
        choices=LifecycleStatusChoices,
        label=_('生命周期状态'),
    )
    
    service_order_id = django_filters.ModelChoiceFilter(
        queryset=ServiceOrder.objects.all(),
        label=_('来源工单'),
    )
    
    class Meta:
        model = ResourceLedger
        fields = ['id', 'resource_type', 'resource_id', 'lifecycle_status', 'service_order']
    
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(resource_id__icontains=value) |
            Q(resource_name__icontains=value) |
            Q(service_order__order_no__icontains=value)
        )

"""
NetBox RMS 视图定义

为每个模型实现标准 NetBox 视图集
"""
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from netbox.views import generic

from .models import ServiceOrder, TaskDetail, ResourceLedger
from .tables import ServiceOrderTable, TaskDetailTable, ResourceLedgerTable
from .filtersets import ServiceOrderFilterSet, TaskDetailFilterSet, ResourceLedgerFilterSet
from .forms import (
    ServiceOrderForm, ServiceOrderFilterForm,
    TaskDetailForm, TaskDetailFilterForm,
    ResourceLedgerForm, ResourceLedgerFilterForm,
)


# =============================================================================
# ServiceOrder 视图
# =============================================================================

class ServiceOrderListView(generic.ObjectListView):
    """业务主工单列表视图"""
    
    queryset = ServiceOrder.objects.annotate(
        task_count=Count('tasks')
    ).prefetch_related('tags')
    filterset = ServiceOrderFilterSet
    filterset_form = ServiceOrderFilterForm
    table = ServiceOrderTable


class ServiceOrderView(generic.ObjectView):
    """业务主工单详情视图"""
    
    queryset = ServiceOrder.objects.prefetch_related('tasks', 'resources', 'tags')
    
    def get_extra_context(self, request, instance):
        # 获取关联任务
        tasks_table = TaskDetailTable(instance.tasks.all())
        tasks_table.configure(request)
        
        # 获取关联资源
        resources_table = ResourceLedgerTable(instance.resources.all())
        resources_table.configure(request)
        
        # 获取子工单（变更单）
        child_orders = ServiceOrder.objects.filter(parent_order=instance)
        child_orders_table = ServiceOrderTable(child_orders)
        child_orders_table.configure(request)
        
        return {
            'tasks_table': tasks_table,
            'resources_table': resources_table,
            'child_orders_table': child_orders_table,
        }


class ServiceOrderEditView(generic.ObjectEditView):
    """业务主工单编辑视图"""
    
    queryset = ServiceOrder.objects.all()
    form = ServiceOrderForm


class ServiceOrderDeleteView(generic.ObjectDeleteView):
    """业务主工单删除视图"""
    
    queryset = ServiceOrder.objects.all()


class ServiceOrderBulkDeleteView(generic.BulkDeleteView):
    """业务主工单批量删除视图"""
    
    queryset = ServiceOrder.objects.all()
    filterset = ServiceOrderFilterSet
    table = ServiceOrderTable


# =============================================================================
# TaskDetail 视图
# =============================================================================

class TaskDetailListView(generic.ObjectListView):
    """执行任务详情列表视图"""
    
    queryset = TaskDetail.objects.select_related('service_order').prefetch_related('tags')
    filterset = TaskDetailFilterSet
    filterset_form = TaskDetailFilterForm
    table = TaskDetailTable


class TaskDetailView(generic.ObjectView):
    """执行任务详情详情视图"""
    
    queryset = TaskDetail.objects.select_related('service_order').prefetch_related('tags')


class TaskDetailEditView(generic.ObjectEditView):
    """执行任务详情编辑视图"""
    
    queryset = TaskDetail.objects.all()
    form = TaskDetailForm


class TaskDetailDeleteView(generic.ObjectDeleteView):
    """执行任务详情删除视图"""
    
    queryset = TaskDetail.objects.all()


class TaskDetailBulkDeleteView(generic.BulkDeleteView):
    """执行任务详情批量删除视图"""
    
    queryset = TaskDetail.objects.all()
    filterset = TaskDetailFilterSet
    table = TaskDetailTable


# =============================================================================
# ResourceLedger 视图
# =============================================================================

class ResourceLedgerListView(generic.ObjectListView):
    """资源台账列表视图"""
    
    queryset = ResourceLedger.objects.select_related('service_order').prefetch_related('tags')
    filterset = ResourceLedgerFilterSet
    filterset_form = ResourceLedgerFilterForm
    table = ResourceLedgerTable


class ResourceLedgerView(generic.ObjectView):
    """资源台账详情视图"""
    
    queryset = ResourceLedger.objects.select_related('service_order').prefetch_related('tags')


class ResourceLedgerEditView(generic.ObjectEditView):
    """资源台账编辑视图"""
    
    queryset = ResourceLedger.objects.all()
    form = ResourceLedgerForm


class ResourceLedgerDeleteView(generic.ObjectDeleteView):
    """资源台账删除视图"""
    
    queryset = ResourceLedger.objects.all()


class ResourceLedgerBulkDeleteView(generic.BulkDeleteView):
    """资源台账批量删除视图"""
    
    queryset = ResourceLedger.objects.all()
    filterset = ResourceLedgerFilterSet
    table = ResourceLedgerTable

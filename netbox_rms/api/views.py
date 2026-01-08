"""
NetBox RMS REST API 视图集
"""
from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from ..models import ServiceOrder, TaskDetail, ResourceLedger, ResourceCheckResult
from ..filtersets import ServiceOrderFilterSet, TaskDetailFilterSet, ResourceLedgerFilterSet, ResourceCheckResultFilterSet
from .serializers import ServiceOrderSerializer, TaskDetailSerializer, ResourceLedgerSerializer, ResourceCheckResultSerializer


class ServiceOrderViewSet(NetBoxModelViewSet):
    """业务主工单 API 视图集"""
    
    queryset = ServiceOrder.objects.annotate(
        task_count=Count('tasks'),
        resource_count=Count('resources'),
    ).prefetch_related('tags')
    serializer_class = ServiceOrderSerializer
    filterset_class = ServiceOrderFilterSet


class TaskDetailViewSet(NetBoxModelViewSet):
    """执行任务详情 API 视图集"""
    
    queryset = TaskDetail.objects.select_related('service_order').prefetch_related('tags')
    serializer_class = TaskDetailSerializer
    filterset_class = TaskDetailFilterSet


class ResourceLedgerViewSet(NetBoxModelViewSet):
    """资源台账 API 视图集"""
    
    queryset = ResourceLedger.objects.select_related('service_order').prefetch_related('tags')
    serializer_class = ResourceLedgerSerializer
    filterset_class = ResourceLedgerFilterSet


class ResourceCheckResultViewSet(NetBoxModelViewSet):
    """资源核查结果 API 视图集"""
    
    queryset = ResourceCheckResult.objects.select_related('service_order').prefetch_related('tags')
    serializer_class = ResourceCheckResultSerializer
    filterset_class = ResourceCheckResultFilterSet

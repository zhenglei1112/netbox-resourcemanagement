"""
NetBox RMS REST API 序列化器
"""
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer

from ..models import ServiceOrder, TaskDetail, ResourceLedger, ResourceCheckResult



class ResourceCheckResultSerializer(NetBoxModelSerializer):
    """资源核查结果序列化器"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_rms-api:resourcecheckresult-detail',
    )
    
    # service_order ID 引用即可，因为通常是主表查子表
    service_order = serializers.PrimaryKeyRelatedField(queryset=ServiceOrder.objects.all())

    class Meta:
        model = ResourceCheckResult
        fields = [
            'id', 'url', 'display', 'service_order',
            'check_result', 'unavailable_reasons', 'description',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]


class ServiceOrderSerializer(NetBoxModelSerializer):
    """业务主工单序列化器"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_rms-api:serviceorder-detail',
    )
    
    tenant = TenantSerializer(nested=True)
    
    parent_order = serializers.PrimaryKeyRelatedField(
        queryset=ServiceOrder.objects.all(),
        required=False,
        allow_null=True,
    )
    
    # 嵌套显示核查结果（只读）
    check_result_obj = ResourceCheckResultSerializer(read_only=True)
    
    task_count = serializers.IntegerField(read_only=True)
    resource_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ServiceOrder
        fields = [
            'id', 'url', 'display',
            'order_no', 'tenant', 'project_report_code', 'project_approval_code',
            'contract_code', 'confirmation_status',
            'sales_contact',
            'business_manager', 'internal_participant',
            'apply_date', 'deadline_date', 'billing_start_date',
            'parent_order', 'special_notes',
            'check_type', 'check_data',
            'check_result_obj', # 输出对象
            'comments',
            'task_count', 'resource_count',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'order_no', 'tenant']


class TaskDetailSerializer(NetBoxModelSerializer):
    """执行任务详情序列化器"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_rms-api:taskdetail-detail',
    )
    
    service_order = ServiceOrderSerializer(nested=True)
    
    class Meta:
        model = TaskDetail
        fields = [
            'id', 'url', 'display', 'service_order',
            'task_type', 'execution_status', 'execution_department', 'assignee',
            'feedback_data',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'task_type']


class ResourceLedgerSerializer(NetBoxModelSerializer):
    """资源台账序列化器"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_rms-api:resourceledger-detail',
    )
    
    service_order = ServiceOrderSerializer(nested=True)
    
    class Meta:
        model = ResourceLedger
        fields = [
            'id', 'url', 'display', 'service_order',
            'resource_type', 'resource_id', 'resource_name',
            'snapshot',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'resource_type', 'resource_id']

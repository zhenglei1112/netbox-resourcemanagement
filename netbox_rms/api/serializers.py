"""
NetBox RMS REST API 序列化器
"""
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from ..models import ServiceOrder, TaskDetail, ResourceLedger


class ServiceOrderSerializer(NetBoxModelSerializer):
    """业务主工单序列化器"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_rms-api:serviceorder-detail',
    )
    
    parent_order = serializers.PrimaryKeyRelatedField(
        queryset=ServiceOrder.objects.all(),
        required=False,
        allow_null=True,
    )
    
    task_count = serializers.IntegerField(read_only=True)
    resource_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ServiceOrder
        fields = [
            'id', 'url', 'display',
            'order_no', 'customer_name', 'project_code', 'sales_contact',
            'apply_date', 'deadline_date', 'billing_start_date',
            'parent_order', 'comments',
            'task_count', 'resource_count',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'order_no', 'customer_name']


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
            # 基础信息
            'task_type', 'lifecycle_status', 'execution_status',
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
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'task_type', 'lifecycle_status']


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
            'lifecycle_status', 'snapshot',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'resource_type', 'resource_id', 'lifecycle_status']

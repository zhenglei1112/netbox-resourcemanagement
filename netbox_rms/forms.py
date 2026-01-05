"""
NetBox RMS 表单定义

用于创建和编辑数据的 Django 表单
"""
import json
from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, CommentField
from utilities.forms.rendering import FieldSet
from dcim.models import Site

from .models import ServiceOrder, TaskDetail, ResourceLedger
from tenancy.models import Tenant
from .choices import (
    TaskTypeChoices,
    LifecycleStatusChoices,
    ExecutionStatusChoices,
    ResourceTypeChoices,
    InternalParticipantChoices,
    ResourceCheckTypeChoices,
    BandwidthChoices,
    InterfaceTypeChoices,
    TransmissionCheckResultChoices,
    TransmissionUnavailableReasonChoices,
    FiberCheckResultChoices,
    FiberUnavailableReasonChoices,
    ColocationCheckResultChoices,
    ColocationUnavailableReasonChoices,
    ColocationDeviceTypeChoices,
)


# =============================================================================
# ServiceOrder 表单
# =============================================================================

class ServiceOrderForm(NetBoxModelForm):
    """业务主工单表单"""
    
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        label=_('客户单位'),
    )
    
    parent_order = DynamicModelChoiceField(
        queryset=ServiceOrder.objects.all(),
        required=False,
        label=_('关联原单号'),
        help_text=_('变更单必须关联原调配单'),
    )
    
    comments = CommentField()
    
    # 显式定义 check_type 字段
    check_type = forms.ChoiceField(
        choices=[('', '---------')] + list(ResourceCheckTypeChoices.CHOICES),
        required=False,
        label=_('核查业务类别'),
    )
    
    # ========== 资源核查可视化字段 ==========
    # 传输专线 & 光缆光纤公共字段
    check_quantity = forms.IntegerField(
        required=False,
        min_value=1,
        label=_('数量'),
    )
    
    check_site_a = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('A端站点'),
    )
    
    check_site_z = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Z端站点'),
    )
    
    check_needs_protection = forms.BooleanField(
        required=False,
        label=_('需要保护'),
    )
    
    check_interface_type = forms.ChoiceField(
        choices=[('', '---------')] + list(InterfaceTypeChoices.CHOICES),
        required=False,
        label=_('接口类型'),
    )
    
    # 传输专线专属
    check_bandwidth = forms.ChoiceField(
        choices=[('', '---------')] + list(BandwidthChoices.CHOICES),
        required=False,
        label=_('带宽'),
    )
    
    # 托管专属
    check_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('机房'),
    )
    
    check_egress_fiber_cores = forms.IntegerField(
        required=False,
        min_value=1,
        label=_('出局纤芯数'),
    )
    
    # 托管设备信息 (JSON 格式存储多设备)
    check_devices_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=_('托管设备数据'),
    )
    
    # ========== 核查结果选择字段 ==========
    # 传输专线核查结果
    check_result_transmission = forms.ChoiceField(
        choices=[('', '---------')] + list(TransmissionCheckResultChoices.CHOICES),
        required=False,
        label=_('核查结果'),
    )
    
    # 光缆光纤核查结果
    check_result_fiber = forms.ChoiceField(
        choices=[('', '---------')] + list(FiberCheckResultChoices.CHOICES),
        required=False,
        label=_('核查结果'),
    )
    
    # 托管业务核查结果
    check_result_colocation = forms.ChoiceField(
        choices=[('', '---------')] + list(ColocationCheckResultChoices.CHOICES),
        required=False,
        label=_('核查结果'),
    )
    
    # 传输专线不具备原因（多选）
    check_unavailable_reasons_transmission = forms.MultipleChoiceField(
        choices=TransmissionUnavailableReasonChoices.CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label=_('不具备原因'),
    )
    
    # 光缆光纤不具备原因（多选）
    check_unavailable_reasons_fiber = forms.MultipleChoiceField(
        choices=FiberUnavailableReasonChoices.CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label=_('不具备原因'),
    )
    
    # 托管不具备原因（多选）
    check_unavailable_reasons = forms.MultipleChoiceField(
        choices=ColocationUnavailableReasonChoices.CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label=_('不具备原因'),
    )
    
    fieldsets = (
        FieldSet(
            'order_no', 'tenant', 'project_code', 'sales_contact',
            'business_manager', 'internal_participant',
            'apply_date', 'deadline_date',
            name=_('申请信息'),
        ),
        FieldSet(
            'check_type',
            'check_bandwidth', 'check_quantity', 'check_site_a', 'check_site_z',
            'check_needs_protection', 'check_interface_type',
            'check_site', 'check_egress_fiber_cores',
            name=_('资源核查'),
        ),
        FieldSet(
            'check_result_transmission', 'check_result_fiber', 'check_result_colocation',
            'check_unavailable_reasons_transmission', 'check_unavailable_reasons_fiber', 'check_unavailable_reasons',
            name=_('核查结果'),
        ),
        FieldSet('tags', name=_('标签')),
    )
    
    class Meta:
        model = ServiceOrder
        fields = [
            'order_no', 'tenant', 'project_code', 'sales_contact',
            'business_manager', 'internal_participant',
            'apply_date', 'deadline_date', 'billing_start_date',
            'parent_order',
            'comments', 'tags',
        ]
        widgets = {
            'apply_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline_date': forms.DateInput(attrs={'type': 'date'}),
            'billing_start_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 从 check_data 中解析初始值
        if self.instance and self.instance.pk:
            data = self.instance.check_data or {}
            if data:
                self.initial['check_quantity'] = data.get('quantity')
                self.initial['check_bandwidth'] = data.get('bandwidth')
                self.initial['check_needs_protection'] = data.get('needs_protection', False)
                self.initial['check_interface_type'] = data.get('interface_type')
                self.initial['check_egress_fiber_cores'] = data.get('egress_fiber_cores')
                
                # 站点 ID 转换
                if data.get('site_a_id'):
                    self.initial['check_site_a'] = data.get('site_a_id')
                if data.get('site_z_id'):
                    self.initial['check_site_z'] = data.get('site_z_id')
                if data.get('site_id'):
                    self.initial['check_site'] = data.get('site_id')
                
                # 设备列表 - 同时设置 initial 和 field widget 属性
                if data.get('devices'):
                    devices_json = json.dumps(data.get('devices'))
                    self.initial['check_devices_json'] = devices_json
                    self.fields['check_devices_json'].initial = devices_json
        
        # 加载核查类型和结果到对应字段
        if self.instance and self.instance.pk:
            check_type = self.instance.check_type or ''
            check_result = self.instance.check_result or ''
            
            # 加载核查类型
            self.initial['check_type'] = check_type
            
            # 加载核查结果到对应字段
            if check_type == 'transmission':
                self.initial['check_result_transmission'] = check_result
            elif check_type == 'fiber':
                self.initial['check_result_fiber'] = check_result
            elif check_type == 'colocation':
                self.initial['check_result_colocation'] = check_result
            
            # 加载不具备原因
            reasons = self.instance.unavailable_reasons
            if reasons and isinstance(reasons, list):
                self.initial['check_unavailable_reasons'] = reasons
    
    def clean(self):
        cleaned_data = super().clean()
        
        # 使用 self.cleaned_data 而不是 super().clean() 的返回值
        if cleaned_data is None:
            cleaned_data = getattr(self, 'cleaned_data', {}) or {}
        
        # 直接从 POST 数据获取 check_type（绕过表单字段验证问题）
        check_type = self.data.get('check_type') or ''
        cleaned_data['check_type'] = check_type
        
        # 构建 check_data JSON
        check_data = {}
        
        if check_type == 'transmission':
            check_data['bandwidth'] = cleaned_data.get('check_bandwidth')
            check_data['quantity'] = cleaned_data.get('check_quantity')
            check_data['needs_protection'] = cleaned_data.get('check_needs_protection', False)
            check_data['interface_type'] = cleaned_data.get('check_interface_type')
            
            site_a = cleaned_data.get('check_site_a')
            site_z = cleaned_data.get('check_site_z')
            if site_a:
                check_data['site_a_id'] = site_a.pk
                check_data['site_a_name'] = site_a.name
            if site_z:
                check_data['site_z_id'] = site_z.pk
                check_data['site_z_name'] = site_z.name
                
        elif check_type == 'fiber':
            check_data['quantity'] = cleaned_data.get('check_quantity')
            check_data['needs_protection'] = cleaned_data.get('check_needs_protection', False)
            check_data['interface_type'] = cleaned_data.get('check_interface_type')
            
            site_a = cleaned_data.get('check_site_a')
            site_z = cleaned_data.get('check_site_z')
            if site_a:
                check_data['site_a_id'] = site_a.pk
                check_data['site_a_name'] = site_a.name
            if site_z:
                check_data['site_z_id'] = site_z.pk
                check_data['site_z_name'] = site_z.name
                
        elif check_type == 'colocation':
            site = cleaned_data.get('check_site')
            if site:
                check_data['site_id'] = site.pk
                check_data['site_name'] = site.name
            check_data['egress_fiber_cores'] = cleaned_data.get('check_egress_fiber_cores')
            
            # 解析设备列表
            devices_json = cleaned_data.get('check_devices_json')
            if devices_json:
                try:
                    check_data['devices'] = json.loads(devices_json)
                except json.JSONDecodeError:
                    check_data['devices'] = []
        
        cleaned_data['check_data'] = check_data
        
        # 根据 check_type 获取对应的核查结果
        if check_type == 'transmission':
            cleaned_data['check_result'] = cleaned_data.get('check_result_transmission', '')
        elif check_type == 'fiber':
            cleaned_data['check_result'] = cleaned_data.get('check_result_fiber', '')
        elif check_type == 'colocation':
            cleaned_data['check_result'] = cleaned_data.get('check_result_colocation', '')
            # 处理不具备原因
            cleaned_data['unavailable_reasons'] = cleaned_data.get('check_unavailable_reasons', [])
        else:
            cleaned_data['check_result'] = ''
        
        return cleaned_data
    
    def save(self, commit=True):
        import json
        instance = super().save(commit=False)
        
        # 直接从 POST 数据获取核查字段
        check_type = self.data.get('check_type', '')
        
        # 构建 check_data
        check_data = {}
        
        # 辅助函数：从 POST 数据获取站点信息
        from dcim.models import Site
        def get_site_info(field_name):
            site_id = self.data.get(field_name)
            if site_id:
                try:
                    site = Site.objects.get(pk=int(site_id))
                    return {'id': site.pk, 'name': site.name}
                except (Site.DoesNotExist, ValueError):
                    pass
            return None
        
        unavailable_reasons = []
        
        if check_type == 'transmission':
            check_data['bandwidth'] = self.data.get('check_bandwidth', '')
            check_data['quantity'] = int(self.data.get('check_quantity') or 0) or None
            check_data['needs_protection'] = bool(self.data.get('check_needs_protection'))
            check_data['interface_type'] = self.data.get('check_interface_type', '')
            
            site_a_info = get_site_info('check_site_a')
            site_z_info = get_site_info('check_site_z')
            if site_a_info:
                check_data['site_a_id'] = site_a_info['id']
                check_data['site_a_name'] = site_a_info['name']
            if site_z_info:
                check_data['site_z_id'] = site_z_info['id']
                check_data['site_z_name'] = site_z_info['name']
            check_result = self.data.get('check_result_transmission', '')
            # 传输专线不具备原因（多选列表）
            unavailable_reasons = self.data.getlist('check_unavailable_reasons_transmission', [])
            
        elif check_type == 'fiber':
            check_data['quantity'] = int(self.data.get('check_quantity') or 0) or None
            check_data['needs_protection'] = bool(self.data.get('check_needs_protection'))
            check_data['interface_type'] = self.data.get('check_interface_type', '')
            
            site_a_info = get_site_info('check_site_a')
            site_z_info = get_site_info('check_site_z')
            if site_a_info:
                check_data['site_a_id'] = site_a_info['id']
                check_data['site_a_name'] = site_a_info['name']
            if site_z_info:
                check_data['site_z_id'] = site_z_info['id']
                check_data['site_z_name'] = site_z_info['name']
            check_result = self.data.get('check_result_fiber', '')
            # 光缆光纤不具备原因（多选列表）
            unavailable_reasons = self.data.getlist('check_unavailable_reasons_fiber', [])
            
        elif check_type == 'colocation':
            site_info = get_site_info('check_site')
            if site_info:
                check_data['site_id'] = site_info['id']
                check_data['site_name'] = site_info['name']
            check_data['egress_fiber_cores'] = int(self.data.get('check_egress_fiber_cores') or 0) or None
            devices_json = self.data.get('check_devices_json', '')
            if devices_json:
                try:
                    check_data['devices'] = json.loads(devices_json)
                except json.JSONDecodeError:
                    check_data['devices'] = []
            check_result = self.data.get('check_result_colocation', '')
            # 托管业务不具备原因（多选列表）
            unavailable_reasons = self.data.getlist('check_unavailable_reasons', [])
        else:
            check_result = ''
        
        # 保存到实例
        instance.check_type = check_type
        instance.check_data = check_data
        instance.check_result = check_result
        instance.unavailable_reasons = unavailable_reasons
        
        if commit:
            instance.save()
            self.save_m2m()
            
            # 手动处理标签
            tag_ids = self.data.getlist('tags')
            if tag_ids:
                from extras.models import Tag
                tags = Tag.objects.filter(pk__in=tag_ids)
                instance.tags.set(tags)
        
        return instance


class ServiceOrderFilterForm(NetBoxModelFilterSetForm):
    """业务主工单过滤表单"""
    
    model = ServiceOrder
    
    order_no = forms.CharField(
        required=False,
        label=_('业务单号'),
    )
    
    tenant_id = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('客户单位'),
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

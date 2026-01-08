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

from .models import ServiceOrder, TaskDetail, ResourceLedger, ResourceCheckResult
from tenancy.models import Tenant
from django.conf import settings
from django.contrib.auth import get_user_model
from .choices import (
    TaskTypeChoices,
    ExecutionStatusChoices,
    ExecutionDepartmentChoices,
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
    ConfirmationStatusChoices,
    AddMethodChoices,
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
    
    project_report_code = forms.CharField(
        required=False,
        label=_('项目报备编号'),
    )

    project_approval_code = forms.CharField(
        required=False,
        label=_('立项编号'),
    )

    contract_code = forms.CharField(
        required=False,
        label=_('合同编号'),
    )

    confirmation_status = forms.ChoiceField(
        choices=[('', '---------')] + list(ConfirmationStatusChoices.CHOICES),
        required=False,
        label=_('确认执行状态'),
    )



    special_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label=_('特殊情况说明'),
    )
    
    comments = CommentField()
    
    # 显式定义 check_type 字段
    check_type = forms.ChoiceField(
        choices=[('', '---------')] + [(c[0], c[1]) for c in ResourceCheckTypeChoices.CHOICES],
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
        choices=[('', '---------')] + [(c[0], c[1]) for c in InterfaceTypeChoices.CHOICES],
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
    

    
    fieldsets = (
        FieldSet(
            'order_no', 'tenant', 'sales_contact',
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
            'project_report_code', 'project_approval_code', 'contract_code', 'confirmation_status',
            'billing_start_date', 'special_notes',
            name=_('执行信息'),
        ),

        FieldSet('tags', name=_('标签')),
    )
    
    class Meta:
        model = ServiceOrder
        fields = [
            'order_no', 'tenant', 'project_report_code', 'project_approval_code',
            'contract_code', 'confirmation_status',
            'sales_contact',
            'business_manager', 'internal_participant',
            'apply_date', 'deadline_date', 'billing_start_date',
            'parent_order', 'special_notes',
            'comments', 'tags',
        ]
        widgets = {
            'apply_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline_date': forms.DateInput(attrs={'type': 'date'}),
            'billing_start_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.initial['check_type'] = self.instance.check_type

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
        # 保存到实例
        instance.check_type = check_type
        instance.check_data = check_data
        
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

    assignee = DynamicModelChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('执行人'),
    )

    # ========== 执行反馈信息字段 ==========
    # 公共字段
    fb_config_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('业务配置日期'),
    )
    fb_test_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('连通测试日期'),
    )
    fb_remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label=_('反馈备注'),
    )

    # 传输专线业务
    fb_trans_is_card_added = forms.BooleanField(required=False, label=_('增加了板卡'))
    fb_trans_card_add_method = forms.ChoiceField(
        choices=[('', '---------')] + list(AddMethodChoices.CHOICES),
        required=False,
        label=_('板卡增加方式'),
    )
    fb_trans_card_add_desc = forms.CharField(required=False, label=_('板卡增加说明'))
    
    fb_trans_is_module_added = forms.BooleanField(required=False, label=_('增加了模块'))
    fb_trans_module_add_method = forms.ChoiceField(
        choices=[('', '---------')] + list(AddMethodChoices.CHOICES),
        required=False,
        label=_('模块增加方式'),
    )
    fb_trans_module_add_desc = forms.CharField(required=False, label=_('模块增加说明'))
    
    fb_trans_circuits_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=_('电路信息数据'),
    )

    # 光缆光纤业务
    fb_fiber_core_count = forms.IntegerField(required=False, label=_('纤芯数量'))
    
    fb_fiber_site_a = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('A端站点'),
    )
    fb_fiber_odf_a = forms.CharField(required=False, label=_('A端ODF信息'))
    fb_fiber_desc_a = forms.CharField(required=False, label=_('A端说明'))
    
    fb_fiber_site_z = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Z端站点'),
    )
    fb_fiber_odf_z = forms.CharField(required=False, label=_('Z端ODF信息'))
    fb_fiber_desc_z = forms.CharField(required=False, label=_('Z端说明'))

    # 托管业务
    fb_colocation_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('机房站点'),
    )
    fb_colocation_info_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=_('托管信息数据'),
    )
    fb_colocation_cable_count = forms.IntegerField(required=False, label=_('出局缆数量'))
    fb_colocation_cable_odf = forms.CharField(required=False, label=_('出局缆ODF信息'))
    
    fieldsets = (
        FieldSet(
            'service_order', 'task_type', 'execution_status', 'execution_department',
            'assignee',
            name=_('基础信息'),
        ),
        FieldSet(
            'fb_trans_is_card_added', 'fb_trans_card_add_method', 'fb_trans_card_add_desc',
            'fb_trans_is_module_added', 'fb_trans_module_add_method', 'fb_trans_module_add_desc',
            name=_('传输反馈'),
        ),
        FieldSet(
            'fb_fiber_core_count', 
            'fb_fiber_site_a', 'fb_fiber_odf_a', 'fb_fiber_desc_a',
            'fb_fiber_site_z', 'fb_fiber_odf_z', 'fb_fiber_desc_z',
            name=_('光缆反馈'),
        ),
        FieldSet(
            'fb_colocation_site', 'fb_colocation_cable_count', 'fb_colocation_cable_odf',
            name=_('托管反馈'),
        ),
        FieldSet(
            'fb_config_date', 'fb_test_date', 'fb_remarks',
            name=_('执行结果汇总'),
        ),
        FieldSet(
            'tags',
            name=_('其他信息')
        ),
    )
    
    class Meta:
        model = TaskDetail
        fields = [
            'service_order', 'task_type', 'execution_status', 'execution_department',
            'assignee', 'comments', 'tags',
            # 临时字段不需要在Meta.fields中声明，除非它们是模型字段。
            # 但这里我们主要靠 clean/save 处理，不需要列在这里，
            # 不过为了 Standard ModelForm validation，如果不列在这里可能会被忽略？
            # NetBoxModelForm 可能会过滤掉非 model 字段。
            # 通常的做法是 override save 和 init，字段声明在类级别即可。
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 初始化反馈字段
        if self.instance and self.instance.pk and self.instance.feedback_data:
            fb = self.instance.feedback_data
            
            self.initial['fb_config_date'] = fb.get('config_date')
            self.initial['fb_test_date'] = fb.get('test_date')
            self.initial['fb_remarks'] = fb.get('remarks')
            
            # 传输
            trans = fb.get('transmission', {})
            self.initial['fb_trans_is_card_added'] = trans.get('is_card_added')
            self.initial['fb_trans_card_add_method'] = trans.get('card_add_method')
            self.initial['fb_trans_card_add_desc'] = trans.get('card_add_desc')
            self.initial['fb_trans_is_module_added'] = trans.get('is_module_added')
            self.initial['fb_trans_module_add_method'] = trans.get('module_add_method')
            self.initial['fb_trans_module_add_desc'] = trans.get('module_add_desc')
            if trans.get('circuits'):
                self.initial['fb_trans_circuits_json'] = json.dumps(trans.get('circuits'))
                
            # 光缆
            fiber = fb.get('fiber', {})
            self.initial['fb_fiber_core_count'] = fiber.get('core_count')
            self.initial['fb_fiber_odf_a'] = fiber.get('odf_a')
            self.initial['fb_fiber_desc_a'] = fiber.get('desc_a')
            self.initial['fb_fiber_odf_z'] = fiber.get('odf_z')
            self.initial['fb_fiber_desc_z'] = fiber.get('desc_z')
            if fiber.get('site_a_id'):
                self.initial['fb_fiber_site_a'] = fiber.get('site_a_id')
            if fiber.get('site_z_id'):
                self.initial['fb_fiber_site_z'] = fiber.get('site_z_id')
                
            # 托管
            colo = fb.get('colocation', {})
            self.initial['fb_colocation_cable_count'] = colo.get('cable_count')
            self.initial['fb_colocation_cable_odf'] = colo.get('cable_odf')
            if colo.get('site_id'):
                self.initial['fb_colocation_site'] = colo.get('site_id')
            if colo.get('devices'):
                self.initial['fb_colocation_info_json'] = json.dumps(colo.get('devices'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 构建 feedback_data
        fb = {
            'config_date': str(self.cleaned_data.get('fb_config_date') or ''),
            'test_date': str(self.cleaned_data.get('fb_test_date') or ''),
            'remarks': self.cleaned_data.get('fb_remarks', ''),
        }
        
        # 传输
        circuits = []
        if self.cleaned_data.get('fb_trans_circuits_json'):
            try:
                circuits = json.loads(self.cleaned_data.get('fb_trans_circuits_json'))
            except:
                pass
                
        fb['transmission'] = {
            'is_card_added': self.cleaned_data.get('fb_trans_is_card_added'),
            'card_add_method': self.cleaned_data.get('fb_trans_card_add_method'),
            'card_add_desc': self.cleaned_data.get('fb_trans_card_add_desc'),
            'is_module_added': self.cleaned_data.get('fb_trans_is_module_added'),
            'module_add_method': self.cleaned_data.get('fb_trans_module_add_method'),
            'module_add_desc': self.cleaned_data.get('fb_trans_module_add_desc'),
            'circuits': circuits
        }
        
        # 光缆
        site_a = self.cleaned_data.get('fb_fiber_site_a')
        site_z = self.cleaned_data.get('fb_fiber_site_z')
        fb['fiber'] = {
            'core_count': self.cleaned_data.get('fb_fiber_core_count'),
            'site_a_id': site_a.pk if site_a else None,
            'site_a_name': site_a.name if site_a else '',
            'odf_a': self.cleaned_data.get('fb_fiber_odf_a'),
            'desc_a': self.cleaned_data.get('fb_fiber_desc_a'),
            'site_z_id': site_z.pk if site_z else None,
            'site_z_name': site_z.name if site_z else '',
            'odf_z': self.cleaned_data.get('fb_fiber_odf_z'),
            'desc_z': self.cleaned_data.get('fb_fiber_desc_z'),
        }
        
        # 托管
        site_colo = self.cleaned_data.get('fb_colocation_site')
        devices = []
        if self.cleaned_data.get('fb_colocation_info_json'):
            try:
                devices = json.loads(self.cleaned_data.get('fb_colocation_info_json'))
            except:
                pass
                
        fb['colocation'] = {
            'site_id': site_colo.pk if site_colo else None,
            'site_name': site_colo.name if site_colo else '',
            'cable_count': self.cleaned_data.get('fb_colocation_cable_count'),
            'cable_odf': self.cleaned_data.get('fb_colocation_cable_odf'),
            'devices': devices
        }
        
        instance.feedback_data = fb
        
        if commit:
            instance.save()
            self.save_m2m()
            
        return instance


class TaskDetailFilterForm(NetBoxModelFilterSetForm):
    """执行任务详情过滤表单"""
    
    model = TaskDetail
    
    task_type = forms.MultipleChoiceField(
        choices=TaskTypeChoices,
        required=False,
        label=_('任务类型'),
    )
    
    execution_status = forms.MultipleChoiceField(
        choices=ExecutionStatusChoices,
        required=False,
        label=_('执行状态'),
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
            'snapshot',
            name=_('快照数据'),
        ),
    )
    
    class Meta:
        model = ResourceLedger
        fields = [
            'service_order', 'resource_type', 'resource_id', 'resource_name',
            'snapshot', 'comments', 'tags',
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
    
    resource_id = forms.CharField(
        required=False,
        label=_('资源标识'),
    )


# =============================================================================
# ResourceCheckResult 表单
# =============================================================================

class ResourceCheckResultForm(NetBoxModelForm):
    """资源核查结果表单"""
    
    service_order = DynamicModelChoiceField(
        queryset=ServiceOrder.objects.all(),
        label=_('所属工单'),
        required=True
    )
    
    # 使用通过 ChoiceField，选项在 __init__ 中动态设置
    check_result = forms.ChoiceField(
        choices=[],
        required=False,
        label=_('核查结果'),
    )
    
    unavailable_reasons = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label=_('不具备原因'),
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label=_('说明'),
    )
    
    fieldsets = (
        FieldSet(
            'service_order', 'check_result', 'unavailable_reasons', 'description',
            name=_('核查结果详情'),
        ),
    )
    
    class Meta:
        model = ResourceCheckResult
        fields = [
            'service_order', 'check_result', 'unavailable_reasons', 'description', 'tags'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. 获取关联的 ServiceOrder
        service_order = None
        
        # 情况 A: 编辑现有对象
        if self.instance.pk and hasattr(self.instance, 'service_order'):
            service_order = self.instance.service_order
        
        # 情况 B: 新建对象，从 initial 获取
        if not service_order and 'service_order' in self.initial:
            so_val = self.initial['service_order']
            if isinstance(so_val, ServiceOrder):
                service_order = so_val
            elif so_val:
                try:
                    service_order = ServiceOrder.objects.get(pk=so_val)
                except (ServiceOrder.DoesNotExist, ValueError):
                    pass
        
        # 情况 C: 新建对象，从 POST data 获取 (表单校验失败重绘时)
        if not service_order and self.data.get('service_order'):
             try:
                service_order = ServiceOrder.objects.get(pk=self.data.get('service_order'))
             except (ServiceOrder.DoesNotExist, ValueError):
                pass

        # 2. 根据 ServiceOrder 的 check_type 动态设置 choices
        if service_order:
            check_type = service_order.check_type
            
            if check_type == 'transmission':
                self.fields['check_result'].choices = [('', '---------')] + [(c[0], c[1]) for c in TransmissionCheckResultChoices.CHOICES]
                self.fields['unavailable_reasons'].choices = [(c[0], c[1]) for c in TransmissionUnavailableReasonChoices.CHOICES]
            elif check_type == 'fiber':
                self.fields['check_result'].choices = [('', '---------')] + [(c[0], c[1]) for c in FiberCheckResultChoices.CHOICES]
                self.fields['unavailable_reasons'].choices = [(c[0], c[1]) for c in FiberUnavailableReasonChoices.CHOICES]
            elif check_type == 'colocation':
                self.fields['check_result'].choices = [('', '---------')] + [(c[0], c[1]) for c in ColocationCheckResultChoices.CHOICES]
                self.fields['unavailable_reasons'].choices = [(c[0], c[1]) for c in ColocationUnavailableReasonChoices.CHOICES]
            else:
                # 未知或无类型
                self.fields['check_result'].choices = [('', '---------')]
                self.fields['unavailable_reasons'].choices = []
        else:
            # 无法确定工单，显示空选项或默认选项
             self.fields['check_result'].choices = [('', '请先选择工单')]
             self.fields['unavailable_reasons'].choices = []


class ResourceCheckResultFilterForm(NetBoxModelFilterSetForm):
    """资源核查结果过滤表单"""
    model = ResourceCheckResult
    
    service_order = DynamicModelChoiceField(
        queryset=ServiceOrder.objects.all(),
        required=False,
        label=_('所属工单'),
    )
    
    check_result = forms.CharField(
        required=False,
        label=_('核查结果')
    )

"""
NetBox RMS 数据模型

定义三个核心模型：
- ServiceOrder: 业务主工单
- TaskDetail: 执行任务详情
- ResourceLedger: 资源台账
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from tenancy.models import Tenant
from dcim.models import Site

from .choices import (
    TaskTypeChoices,
    ExecutionStatusChoices,
    ExecutionDepartmentChoices,
    ServiceTypeChoices,
    InterfaceTypeChoices,
    ResourceTypeChoices,
    ChangeTypeChoices,
    ExternalHandleChoices,
    InternalParticipantChoices,
    ResourceCheckTypeChoices,
    ConfirmationStatusChoices,
)


class ServiceOrder(NetBoxModel):
    """
    业务主工单模型
    
    对应所有纸质单据的"表头"通用信息，如资源核查单、调配单、变更单、托管单。
    """
    
    # 基础信息
    order_no = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('业务单号'),
        help_text=_('唯一业务单号，如 XQ251010001-JX, BG251226001'),
    )
    
    tenant = models.ForeignKey(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='service_orders',
        verbose_name=_('客户单位'),
        help_text=_('从 NetBox 租户中选择'),
    )
    
    project_report_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('项目报备编号'),
    )

    project_approval_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('立项编号'),
    )

    contract_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('合同编号'),
    )
    
    sales_contact = models.CharField(
        max_length=100,
        verbose_name=_('销售负责人'),
    )
    
    business_manager = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('商务负责人'),
        help_text=_('商务对接负责人'),
    )
    
    internal_participant = models.CharField(
        max_length=50,
        choices=InternalParticipantChoices,
        blank=True,
        verbose_name=_('内部参与方'),
        help_text=_('选择内部参与方：市场部、江西分公司、浙江分公司、四川分公司'),
    )
    
    # 时间相关
    apply_date = models.DateField(
        verbose_name=_('申请时间'),
    )
    
    deadline_date = models.DateField(
        verbose_name=_('计划开通时间'),
    )
    
    billing_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('起租日期'),
    )

    # 确认执行状态
    confirmation_status = models.CharField(
        max_length=30,
        choices=ConfirmationStatusChoices,
        blank=True,
        verbose_name=_('确认执行状态'),
    )



    # 特殊情况说明
    special_notes = models.TextField(
        blank=True,
        verbose_name=_('特殊情况说明'),
    )
    
    # 变更追溯
    parent_order = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='child_orders',
        verbose_name=_('关联原单号'),
        help_text=_('变更单必须关联原调配单ID'),
    )
    
    # ========== 资源核查扩展字段 ==========
    check_type = models.CharField(
        max_length=50,
        choices=ResourceCheckTypeChoices,
        blank=True,
        verbose_name=_('核查业务类别'),
        help_text=_('传输专线、光缆光纤、托管'),
    )
    
    check_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('核查数据'),
        help_text=_('存储类型特定的核查属性'),
    )
    

    
    # 备注
    comments = models.TextField(
        blank=True,
        verbose_name=_('备注'),
    )
    
    class Meta:
        ordering = ['-apply_date', '-pk']
        verbose_name = _('业务主工单')
        verbose_name_plural = _('业务主工单')
    
    @property
    def safe_check_data(self):
        """安全获取 check_data，确保返回字典而非 None"""
        return self.check_data if self.check_data else {}
    
    @property
    def check_result(self):
        """兼容性属性：获取关联的核查结果"""
        if hasattr(self, 'check_result_obj'):
            return self.check_result_obj.check_result
        return ''

    @property
    def safe_unavailable_reasons(self):
        """安全获取 unavailable_reasons，确保返回列表而非 None"""
        if hasattr(self, 'check_result_obj'):
            reasons = self.check_result_obj.unavailable_reasons
            return reasons if reasons else []
        return []
    
    @property
    def check_result_display(self):
        """获取核查结果的中文显示"""
        result = self.check_result
        result_mapping = {
            'available': '具备',
            'unavailable': '不具备',
            'need_module': '需增加模块',
            'need_card': '需增加板卡',
        }
        return result_mapping.get(result, result or '')
    
    @property
    def interface_type_display(self):
        """获取接口类型的中文显示"""
        data = self.safe_check_data
        interface_type = data.get('interface_type', '')
        type_mapping = {
            'optical': '光',
            'electrical': '电',
        }
        return type_mapping.get(interface_type, interface_type or '')
    
    @property
    def get_interface_type_color(self):
        """获取接口类型颜色 class"""
        data = self.safe_check_data
        interface_type = data.get('interface_type', '')
        return InterfaceTypeChoices.colors.get(interface_type, 'secondary')
    
    @property
    def get_check_type_color(self):
        """获取业务类别颜色 class"""
        return ResourceCheckTypeChoices.colors.get(self.check_type, 'secondary')

    @property
    def site_a_object(self):
        """获取 A 端站点对象"""
        site_id = self.safe_check_data.get('site_a_id')
        if site_id:
            try:
                return Site.objects.get(pk=site_id)
            except Site.DoesNotExist:
                pass
        return None

    @property
    def site_z_object(self):
        """获取 Z 端站点对象"""
        site_id = self.safe_check_data.get('site_z_id')
        if site_id:
            try:
                return Site.objects.get(pk=site_id)
            except Site.DoesNotExist:
                pass
        return None

    @property
    def colocation_site_object(self):
        """获取托管业务机房对象"""
        site_id = self.safe_check_data.get('site_id')
        if site_id:
            try:
                return Site.objects.get(pk=site_id)
            except Site.DoesNotExist:
                pass
        return None
    
    def __str__(self) -> str:
        return f"{self.order_no} - {self.tenant.name}"
    
    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_rms:serviceorder', args=[self.pk])


class TaskDetail(NetBoxModel):
    """
    执行任务详情模型
    
    支持三种业务场景：
    - 入网/开通: 新业务接入和资源分配
    - 变更: 已有业务的调整和修改
    - 退网/拆机: 业务下线和资源回收
    """
    
    # 关联主工单
    service_order = models.ForeignKey(
        to='ServiceOrder',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('所属主工单'),
    )
    
    # 任务类型
    task_type = models.CharField(
        max_length=50,
        choices=TaskTypeChoices,
        default=TaskTypeChoices.ACTIVATION,
        verbose_name=_('任务类型'),
    )
    
    # 执行状态
    execution_status = models.CharField(
        max_length=50,
        choices=ExecutionStatusChoices,
        default=ExecutionStatusChoices.PENDING,
        verbose_name=_('执行状态'),
    )
    
    # 执行部门
    execution_department = models.CharField(
        max_length=50,
        choices=ExecutionDepartmentChoices,
        blank=True,
        verbose_name=_('执行部门'),
        help_text=_('负责执行此任务的部门'),
    )
    
    feedback_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('执行反馈信息'),
        help_text=_('存储执行后的具体反馈数据'),
    )
    
    assignee = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='rms_tasks',
        blank=True,
        null=True,
        verbose_name=_('执行人'),
    )

    def get_task_type_color(self):
        """获取任务类型颜色"""
        return TaskTypeChoices.colors.get(self.task_type, 'secondary')
    
    def get_execution_status_color(self):
        """获取执行状态颜色"""
        return ExecutionStatusChoices.colors.get(self.execution_status, 'secondary')
    
    def get_execution_department_color(self):
        """获取执行部门颜色"""
        return ExecutionDepartmentChoices.colors.get(self.execution_department, 'secondary')
    

    
    # 备注
    comments = models.TextField(
        blank=True,
        verbose_name=_('备注'),
    )
    
    class Meta:
        ordering = ['-pk']
        verbose_name = _('执行任务详情')
        verbose_name_plural = _('执行任务详情')
    
    def __str__(self) -> str:
        return f"{self.service_order.order_no} - {self.get_task_type_display()}"
    
    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_rms:taskdetail', args=[self.pk])
    
    def clean(self) -> None:
        """业务逻辑校验"""
        super().clean()
        
        # 变更单必须关联原单号
        if self.task_type == TaskTypeChoices.CHANGE:
            if not self.service_order.parent_order:
                raise ValidationError(
                    _('变更类型任务的主工单必须关联原单号')
                )


class ResourceLedger(NetBoxModel):
    """
    资源台账模型
    
    最终形成的资产快照（如一条在用电路、一台托管设备）。
    """
    
    # 关联来源工单
    service_order = models.ForeignKey(
        to='ServiceOrder',
        on_delete=models.PROTECT,
        related_name='resources',
        verbose_name=_('来源工单'),
    )
    
    # 资源基本信息
    resource_type = models.CharField(
        max_length=50,
        choices=ResourceTypeChoices,
        verbose_name=_('资源类型'),
    )
    
    resource_id = models.CharField(
        max_length=100,
        verbose_name=_('资源标识'),
        help_text=_('电路编号/机柜U位/光缆芯数'),
    )
    
    resource_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('资源名称'),
    )
    
    # 资源快照 (JSON 存储详细参数)
    snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('资源快照'),
        help_text=_('存储资源详细参数的快照数据'),
    )
    
    # 备注
    comments = models.TextField(
        blank=True,
        verbose_name=_('备注'),
    )
    
    class Meta:
        ordering = ['-pk']
        verbose_name = _('资源台账')
        verbose_name_plural = _('资源台账')
        unique_together = [['resource_type', 'resource_id']]
    
    def __str__(self) -> str:
        return f"{self.get_resource_type_display()} - {self.resource_id}"
    
    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_rms:resourceledger', args=[self.pk])


class ResourceCheckResult(NetBoxModel):
    """
    资源核查结果模型
    
    独立模型以实现对象级权限控制。
    """
    service_order = models.OneToOneField(
        to='ServiceOrder',
        on_delete=models.CASCADE,
        related_name='check_result_obj',
        verbose_name=_('所属工单'),
    )
    
    check_result = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('核查结果'),
    )
    
    unavailable_reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('不具备原因'),
        help_text=_('不具备时的原因列表'),
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('说明'),
    )
    
    class Meta:
        ordering = ['-pk']
        verbose_name = _('资源核查结果')
        verbose_name_plural = _('资源核查结果')
        
    def __str__(self) -> str:
        return f"Check Result for {self.service_order}"
    
    def get_absolute_url(self) -> str:
        # 暂时返回主工单 URL，或者后续单独的 Edit URL
        return self.service_order.get_absolute_url()
    


    

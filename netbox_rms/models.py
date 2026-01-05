"""
NetBox RMS 数据模型

定义三个核心模型：
- ServiceOrder: 业务主工单
- TaskDetail: 执行任务详情
- ResourceLedger: 资源台账
"""
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from tenancy.models import Tenant

from .choices import (
    TaskTypeChoices,
    LifecycleStatusChoices,
    ExecutionStatusChoices,
    ServiceTypeChoices,
    InterfaceTypeChoices,
    ResourceTypeChoices,
    ChangeTypeChoices,
    ExternalHandleChoices,
    InternalParticipantChoices,
    ResourceCheckTypeChoices,
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
    
    project_code = models.CharField(
        max_length=100,
        verbose_name=_('项目/合同编号'),
        help_text=_('支持双号并行，如 WLGSXS2409001'),
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
        blank=True,
        null=True,
        verbose_name=_('计费起始日期'),
        help_text=_('财务结算依据，来源于核查单确认栏'),
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
    
    check_result = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('核查结果'),
    )
    
    unavailable_reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('不具备原因'),
        help_text=_('托管业务不具备时的原因列表'),
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
    def safe_unavailable_reasons(self):
        """安全获取 unavailable_reasons，确保返回列表而非 None"""
        return self.unavailable_reasons if self.unavailable_reasons else []
    
    @property
    def check_result_display(self):
        """获取核查结果的中文显示"""
        result_mapping = {
            'available': '具备',
            'unavailable': '不具备',
            'need_module': '需增加模块',
            'need_card': '需增加板卡',
        }
        return result_mapping.get(self.check_result, self.check_result or '')
    
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
    
    def __str__(self) -> str:
        return f"{self.order_no} - {self.tenant.name}"
    
    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_rms:serviceorder', args=[self.pk])


class TaskDetail(NetBoxModel):
    """
    执行任务详情模型
    
    根据 task_type 区分显示不同的字段组：
    - 核查/调配: 技术参数 + 运维/管线参数
    - 变更: 变更管理参数
    - 托管: 设备托管参数
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
        default=TaskTypeChoices.ALLOCATION,
        verbose_name=_('任务类型'),
    )
    
    # 双层状态
    lifecycle_status = models.CharField(
        max_length=50,
        choices=LifecycleStatusChoices,
        default=LifecycleStatusChoices.DRAFT,
        verbose_name=_('生命周期状态'),
    )
    
    execution_status = models.CharField(
        max_length=50,
        choices=ExecutionStatusChoices,
        default=ExecutionStatusChoices.PENDING,
        verbose_name=_('执行状态'),
    )
    
    # ========== 场景 1: 技术参数 ==========
    service_type = models.CharField(
        max_length=50,
        choices=ServiceTypeChoices,
        blank=True,
        verbose_name=_('业务类型'),
    )
    
    bandwidth = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('带宽数量'),
        help_text=_('如：1 (2G)'),
    )
    
    protection = models.BooleanField(
        default=False,
        verbose_name=_('是否保护'),
    )
    
    protection_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('保护类型'),
        help_text=_('复用段/通道保护'),
    )
    
    interface_type = models.CharField(
        max_length=50,
        choices=InterfaceTypeChoices,
        blank=True,
        verbose_name=_('接口类型'),
    )
    
    site_a = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('A端接入站点'),
    )
    
    site_z = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Z端接入站点'),
    )
    
    # ========== 场景 2: 运维实施参数 ==========
    circuit_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('电路分配编号'),
        help_text=_('核心逻辑ID，如 256763/02N0690SC'),
    )
    
    dev_model_a = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('A端设备型号'),
        help_text=_('如 OSN9800 西宁'),
    )
    
    slot_a = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('A端板卡/槽位'),
        help_text=_('兼容 12-TnO 或 T220/32 格式'),
    )
    
    port_a = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('A端端口'),
    )
    
    dev_model_z = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Z端设备型号'),
    )
    
    slot_z = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Z端板卡/槽位'),
    )
    
    port_z = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Z端端口'),
    )
    
    config_status = models.BooleanField(
        default=False,
        verbose_name=_('业务配置完成'),
    )
    
    test_status = models.BooleanField(
        default=False,
        verbose_name=_('连通测试完成'),
    )
    
    # ========== 场景 3: 管线实施参数 ==========
    cable_core = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('出局缆芯数'),
        help_text=_('如：出局缆4芯'),
    )
    
    odf_pos = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('ODF位置'),
    )
    
    jump_status = models.BooleanField(
        default=False,
        verbose_name=_('两端跳接完成'),
    )
    
    ext_resource = models.BooleanField(
        default=False,
        verbose_name=_('外购资源'),
    )
    
    ext_contract = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('外购合同编号'),
        help_text=_('若有外购资源必填'),
    )
    
    # ========== 场景 4: 设备托管参数 ==========
    device_brand = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('设备品牌/类型'),
        help_text=_('如：交换机'),
    )
    
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('尺寸 (W*D*H)'),
    )
    
    power_rating = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('功耗'),
    )
    
    rack_u_pos = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('机柜U位'),
        help_text=_('如 U10-U12'),
    )
    
    power_status = models.BooleanField(
        default=False,
        verbose_name=_('安装加电完成'),
    )
    
    # ========== 场景 5: 变更管理参数 ==========
    change_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('变更类型'),
        help_text=_('多选：带宽/开撤/方向/保护/托管'),
    )
    
    old_value = models.TextField(
        blank=True,
        verbose_name=_('原状态'),
        help_text=_('如：原AZ端：14-4'),
    )
    
    new_value = models.TextField(
        blank=True,
        verbose_name=_('变更后状态'),
        help_text=_('如：变更后AZ端：14-10'),
    )
    
    ext_handle = models.CharField(
        max_length=50,
        choices=ExternalHandleChoices,
        blank=True,
        verbose_name=_('外购资源处理'),
    )
    
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
        
        # 外购资源联动校验
        if self.ext_resource and not self.ext_contract:
            raise ValidationError({
                'ext_contract': _('勾选外购资源时，外购合同编号必填'),
            })
        
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
    
    # 生命周期状态
    lifecycle_status = models.CharField(
        max_length=50,
        choices=LifecycleStatusChoices,
        default=LifecycleStatusChoices.ACTIVE,
        verbose_name=_('生命周期状态'),
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
    
    def get_status_color(self) -> str:
        """根据状态返回高亮颜色类"""
        color_map = {
            LifecycleStatusChoices.DRAFT: 'secondary',
            LifecycleStatusChoices.RESERVED: 'info',
            LifecycleStatusChoices.ACTIVE: 'success',
            LifecycleStatusChoices.SUSPENDED: 'warning',
            LifecycleStatusChoices.TERMINATED: 'danger',
        }
        return color_map.get(self.lifecycle_status, 'secondary')

"""
NetBox RMS 选择项定义 (Choices)

定义所有枚举类型字段的选项
"""
from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet


class TaskTypeChoices(ChoiceSet):
    """任务类型选择项"""
    
    VERIFICATION = 'verification'       # 资源核查
    ALLOCATION = 'allocation'           # 资源调配
    CHANGE = 'change'                   # 资源变更
    HOSTING = 'hosting'                 # 设备托管
    
    CHOICES = [
        (VERIFICATION, _('资源核查')),
        (ALLOCATION, _('资源调配')),
        (CHANGE, _('资源变更')),
        (HOSTING, _('设备托管')),
    ]


class LifecycleStatusChoices(ChoiceSet):
    """生命周期状态选择项"""
    
    DRAFT = 'draft'                     # 草稿
    RESERVED = 'reserved'               # 预占
    ACTIVE = 'active'                   # 在用/计费
    SUSPENDED = 'suspended'             # 暂停
    TERMINATED = 'terminated'           # 已拆机
    
    CHOICES = [
        (DRAFT, _('草稿'), 'gray'),
        (RESERVED, _('预占'), 'blue'),
        (ACTIVE, _('在用'), 'green'),
        (SUSPENDED, _('暂停'), 'orange'),
        (TERMINATED, _('已拆机'), 'red'),
    ]


class ExecutionStatusChoices(ChoiceSet):
    """执行状态选择项"""
    
    PENDING = 'pending'                 # 待实施
    PATCHED = 'patched'                 # 已跳接
    CONFIGURED = 'configured'           # 已配置
    CONNECTED = 'connected'             # 已连通
    
    CHOICES = [
        (PENDING, _('待实施'), 'gray'),
        (PATCHED, _('已跳接'), 'blue'),
        (CONFIGURED, _('已配置'), 'cyan'),
        (CONNECTED, _('已连通'), 'green'),
    ]


class ServiceTypeChoices(ChoiceSet):
    """业务类型选择项"""
    
    OTN_10G = '10G'
    OTN_2_5G = '2.5G'
    OTN_GE = 'GE'
    OTN_100G = '100G'
    CABLE = 'cable'
    
    CHOICES = [
        (OTN_10G, '10G'),
        (OTN_2_5G, '2.5G'),
        (OTN_GE, 'GE'),
        (OTN_100G, '100G'),
        (CABLE, _('光缆业务')),
    ]


class InterfaceTypeChoices(ChoiceSet):
    """接口类型选择项"""
    
    ELECTRICAL = 'electrical'
    OPTICAL = 'optical'
    
    CHOICES = [
        (ELECTRICAL, _('电')),
        (OPTICAL, _('光')),
    ]


class ResourceTypeChoices(ChoiceSet):
    """资源类型选择项"""
    
    CIRCUIT = 'circuit'                 # 电路
    HOSTING_DEVICE = 'hosting_device'   # 托管设备
    CABLE = 'cable'                     # 光缆/裸纤
    
    CHOICES = [
        (CIRCUIT, _('电路')),
        (HOSTING_DEVICE, _('托管设备')),
        (CABLE, _('光缆/裸纤')),
    ]


class ChangeTypeChoices(ChoiceSet):
    """变更类型选择项 (多选)"""
    
    BANDWIDTH = 'bandwidth'             # 带宽变更
    TOGGLE = 'toggle'                   # 业务开/撤
    DIRECTION = 'direction'             # 方向变更
    PROTECTION = 'protection'           # 保护变更
    HOSTING = 'hosting'                 # 托管变更
    
    CHOICES = [
        (BANDWIDTH, _('带宽变更')),
        (TOGGLE, _('业务开/撤')),
        (DIRECTION, _('方向变更')),
        (PROTECTION, _('保护变更')),
        (HOSTING, _('托管变更')),
    ]


class ExternalHandleChoices(ChoiceSet):
    """外购资源处理方式选择项"""
    
    CLOSE = 'close'                     # 关闭
    CONTINUE = 'continue'               # 延续
    CHANGE = 'change'                   # 变更
    
    CHOICES = [
        (CLOSE, _('关闭')),
        (CONTINUE, _('延续')),
        (CHANGE, _('变更')),
    ]

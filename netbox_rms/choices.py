"""
NetBox RMS 选择项定义 (Choices)

定义所有枚举类型字段的选项
"""
from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet


class TaskTypeChoices(ChoiceSet):
    """任务类型选择项"""
    
    ACTIVATION = 'activation'           # 入网/开通
    CHANGE = 'change'                   # 变更
    DEACTIVATION = 'deactivation'       # 退网/拆机
    
    CHOICES = [
        (ACTIVATION, _('入网/开通'), 'green'),
        (CHANGE, _('变更'), 'yellow'),
        (DEACTIVATION, _('退网/拆机'), 'red'),
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
        (CONNECTED, _('已连通'), 'teal'),
    ]


class ExecutionDepartmentChoices(ChoiceSet):
    """执行部门选择项"""
    
    PIPELINE = 'pipeline'               # 管线部
    OPERATION = 'operation'             # 运维部
    
    CHOICES = [
        (PIPELINE, _('管线部'), 'orange'),
        (OPERATION, _('运维部'), 'purple'),
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
        (ELECTRICAL, _('电'), 'cyan'),
        (OPTICAL, _('光'), 'purple'),
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


class InternalParticipantChoices(ChoiceSet):
    """内部参与方选择项"""
    
    MARKETING = 'marketing'             # 市场部
    JIANGXI = 'jiangxi'                 # 江西分公司
    ZHEJIANG = 'zhejiang'               # 浙江分公司
    SICHUAN = 'sichuan'                 # 四川分公司
    
    CHOICES = [
        (MARKETING, _('市场部')),
        (JIANGXI, _('江西分公司')),
        (ZHEJIANG, _('浙江分公司')),
        (SICHUAN, _('四川分公司')),
    ]


class ConfirmationStatusChoices(ChoiceSet):
    """确认执行状态"""
    
    EXECUTION_BILLING = 'execution_billing' # 执行（计费）
    EXECUTION_TEST = 'execution_test'       # 执行（测试）
    CANCEL = 'cancel'                       # 取消
    
    CHOICES = [
        (EXECUTION_BILLING, _('执行（计费）')),
        (EXECUTION_TEST, _('执行（测试）')),
        (CANCEL, _('取消')),
    ]


# =============================================================================
# 资源核查相关选择项
# =============================================================================

class ResourceCheckTypeChoices(ChoiceSet):
    """资源核查业务类别"""
    
    TRANSMISSION = 'transmission'       # 传输专线业务
    FIBER = 'fiber'                     # 光缆光纤业务
    COLOCATION = 'colocation'           # 托管业务
    
    CHOICES = [
        (TRANSMISSION, _('传输专线业务'), 'blue'),
        (FIBER, _('光缆光纤业务'), 'orange'),
        (COLOCATION, _('托管业务'), 'purple'),
    ]


class BandwidthChoices(ChoiceSet):
    """带宽选项"""
    
    GE = 'GE'
    G2_5 = '2.5G'
    G10 = '10G'
    G100 = '100G'
    
    CHOICES = [
        (GE, 'GE'),
        (G2_5, '2.5G'),
        (G10, '10G'),
        (G100, '100G'),
    ]


class TransmissionCheckResultChoices(ChoiceSet):
    """传输专线核查结果"""
    
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    
    CHOICES = [
        (AVAILABLE, _('具备')),
        (UNAVAILABLE, _('不具备')),
    ]


class TransmissionUnavailableReasonChoices(ChoiceSet):
    """传输专线不具备原因（多选）"""
    
    WAVELENGTH = 'wavelength'
    MODULE = 'module'
    CARD = 'card'
    PROTECTION = 'protection'
    
    CHOICES = [
        (WAVELENGTH, _('波道不满足')),
        (MODULE, _('模块不满足')),
        (CARD, _('板卡不满足')),
        (PROTECTION, _('成环保护不满足')),
    ]


class FiberCheckResultChoices(ChoiceSet):
    """光缆光纤核查结果"""
    
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    
    CHOICES = [
        (AVAILABLE, _('具备')),
        (UNAVAILABLE, _('不具备')),
    ]


class FiberUnavailableReasonChoices(ChoiceSet):
    """光缆光纤不具备原因（多选）"""
    
    FIBER = 'fiber'
    PROTECTION = 'protection'
    
    CHOICES = [
        (FIBER, _('光纤不满足')),
        (PROTECTION, _('成环保护不满足')),
    ]


class ColocationCheckResultChoices(ChoiceSet):
    """托管业务核查结果"""
    
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    
    CHOICES = [
        (AVAILABLE, _('具备')),
        (UNAVAILABLE, _('不具备')),
    ]


class ColocationUnavailableReasonChoices(ChoiceSet):
    """托管业务不具备原因（多选）"""
    
    CABINET = 'cabinet'
    POWER = 'power'
    SPACE = 'space'
    FIBER = 'fiber'
    
    CHOICES = [
        (CABINET, _('机柜不满足')),
        (POWER, _('配电不满足')),
        (SPACE, _('机柜空间不满足')),
        (FIBER, _('引接纤芯不满足')),
    ]


class ColocationDeviceTypeChoices(ChoiceSet):
    """托管设备类型"""
    
    TRANSMISSION = 'transmission'
    SWITCH = 'switch'
    ROUTER = 'router'
    OTHER = 'other'
    
    CHOICES = [
        (TRANSMISSION, _('传输设备')),
        (SWITCH, _('交换机')),
        (ROUTER, _('路由器')),
        (OTHER, _('其他')),
    ]


class AddMethodChoices(ChoiceSet):
    """增加方式选择项"""
    
    NEW = 'new'           # 新购
    ALLOCATION = 'allocation' # 调配
    OTHER = 'other'       # 其他
    
    CHOICES = [
        (NEW, _('新购')),
        (ALLOCATION, _('调配')),
        (OTHER, _('其他')),
    ]

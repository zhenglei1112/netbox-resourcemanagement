"""
NetBox RMS (Resource Management System) Plugin

传输资源管理系统插件 - 用于数字化管理传输专线及设备托管业务。
"""
from netbox.plugins import PluginConfig


class RMSConfig(PluginConfig):
    """NetBox RMS 插件配置类"""
    
    name = 'netbox_rms'
    verbose_name = '传输资源管理系统'
    description = '用于数字化管理传输专线及设备托管业务的 NetBox 插件'
    version = '0.1.0'
    author = 'NetBox RMS Team'
    author_email = 'admin@example.com'
    base_url = 'rms'
    min_version = '4.0.0'
    max_version = '4.99'
    
    # 默认设置
    default_settings = {
        'enable_external_resource_validation': True,
        'auto_fill_change_order': True,
    }
    
    def ready(self) -> None:
        """插件就绪时注册信号处理器"""
        super().ready()
        from . import signals  # noqa: F401


config = RMSConfig

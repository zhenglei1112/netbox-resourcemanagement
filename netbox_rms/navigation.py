"""
NetBox RMS 导航菜单配置
"""
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


# 业务主工单菜单项
service_order_items = (
    PluginMenuItem(
        link='plugins:netbox_rms:serviceorder_list',
        link_text='业务主工单',
        permissions=['netbox_rms.view_serviceorder'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_rms:serviceorder_add',
                title='新建工单',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_rms.add_serviceorder'],
            ),
        ),
    ),
)

# 执行任务菜单项
task_detail_items = (
    PluginMenuItem(
        link='plugins:netbox_rms:taskdetail_list',
        link_text='执行任务',
        permissions=['netbox_rms.view_taskdetail'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_rms:taskdetail_add',
                title='新建任务',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_rms.add_taskdetail'],
            ),
        ),
    ),
)

# 资源台账菜单项
resource_ledger_items = (
    PluginMenuItem(
        link='plugins:netbox_rms:resourceledger_list',
        link_text='资源台账',
        permissions=['netbox_rms.view_resourceledger'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_rms:resourceledger_add',
                title='新建资源',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_rms.add_resourceledger'],
            ),
        ),
    ),
)

# 主菜单
menu = PluginMenu(
    label='资源管理',
    groups=(
        ('业务工单', service_order_items),
        ('执行管理', task_detail_items),
        ('资源台账', resource_ledger_items),
    ),
    icon_class='mdi mdi-clipboard-list-outline',
)

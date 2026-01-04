# NetBox RMS - 传输资源管理系统插件

基于 NetBox 4.x 的传输资源管理插件，用于数字化管理传输专线及设备托管业务。

## 功能特性

- **业务主工单管理 (ServiceOrder)**：对应所有纸质单据的"表头"通用信息
- **执行任务详情 (TaskDetail)**：核查/调配/变更/托管等具体业务动作
- **资源台账 (ResourceLedger)**：最终形成的资产快照

## 安装

```bash
# 在 NetBox 虚拟环境中
pip install -e /path/to/netbox-resourcemanagement

# 将插件添加到 configuration.py
PLUGINS = ['netbox_rms']

# 运行数据库迁移
python manage.py migrate netbox_rms

# 收集静态文件
python manage.py collectstatic --noinput

# 重启 NetBox
systemctl restart netbox
```

## 开发

本项目遵循 NetBox 4.x 插件开发规范。

## 许可证

Apache-2.0

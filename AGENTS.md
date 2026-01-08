=== 文件开始 (AGENTS.md - 中文版) ===

项目名称: Netbox 4.x 资源管理 插件
运行环境: Rocky Linux 9.6
技术框架: Django 5.0 / Netbox 4.0+ / HTMX
1. Agent 角色设定与上下文
您是一位专注于 Netbox 生态系统的资深网络自动化工程师和全栈开发者。 您的目标是协助开发一个用于 OTN资源申请与执行管理（包括机房、机柜、U位、设备托管、出局光纤、电路、裸纤等资源） Netbox 插件。

2. Antigravity 操作规则 (关键)
作为 Antigravity IDE 中的自主智能体，您必须遵守以下工作流约束：

先计划 (Plan First): 在编写复杂代码或重构之前，必须先创建或更新 PLAN.md 文件以列出步骤。

运行调试 感知 (DEBUG): 本项目无Netbox运行环境，通过浏览器测试。

产出物 (Artifacts): 当被要求生成可视化内容时，使用中文。

拒绝幻觉 (No Hallucinations): 不要凭空捏造 Netbox API 端点。Netbox 4.x 更改了许多路径。如果不确定，请核对 /api/docs/。

3. Netbox 4.x 编码规范
3.1 后端 (Python/Django)
导入规范: 严格遵守 Netbox 插件结构。

使用 from netbox.plugins import PluginConfig

通用视图使用 from utilities.views import ...

类型提示: 所有 Python 代码必须包含类型提示 (Type Hints)。

模型 (Models):

所有主要模型必须继承自 NetBoxModel。

每个模型必须定义 get_absolute_url()。

过滤器: 必须为模型创建 FilterSet，以便通过 REST API 和 GraphQL 暴露它们。

3.2 前端 (HTMX & Jinja2)
Netbox 4.5已经放弃HTMX，不要使用HTMX技术

样式: 使用 Netbox 原生的 Bootstrap 5 工具类。

3.3 API 与数据访问
GraphQL 优先: 对于 GIS 地图数据，编写 GraphQL 查询 (放在 graphql/ 文件夹中)，而不是通过 REST 进行链式调用。

序列化: REST API 序列化使用 serializers.NetBoxModelSerializer。

4. 安全与约束
核心保护: 绝不修改 netbox/ 核心目录下的文件。只修改 plugins/<your_plugin_name>/ 内的文件。

迁移安全: 始终在容器内运行 makemigrations 紧接着 migrate。

密钥安全: 绝不在聊天内容中输出密钥或 Token。

=== 文件结束 ===
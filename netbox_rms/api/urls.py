"""
NetBox RMS REST API URL 路由
"""
from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'netbox_rms-api'

router = NetBoxRouter()
router.register('service-orders', views.ServiceOrderViewSet)
router.register('tasks', views.TaskDetailViewSet)
router.register('resources', views.ResourceLedgerViewSet)

urlpatterns = router.urls

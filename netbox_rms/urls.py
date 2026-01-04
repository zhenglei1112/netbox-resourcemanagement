"""
NetBox RMS URL 路由配置
"""
from django.urls import include, path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from . import views
from .models import ServiceOrder, TaskDetail, ResourceLedger

app_name = 'netbox_rms'

urlpatterns = [
    # =============================================================================
    # ServiceOrder 路由
    # =============================================================================
    path('service-orders/', views.ServiceOrderListView.as_view(), name='serviceorder_list'),
    path('service-orders/add/', views.ServiceOrderEditView.as_view(), name='serviceorder_add'),
    path('service-orders/<int:pk>/', views.ServiceOrderView.as_view(), name='serviceorder'),
    path('service-orders/<int:pk>/edit/', views.ServiceOrderEditView.as_view(), name='serviceorder_edit'),
    path('service-orders/<int:pk>/delete/', views.ServiceOrderDeleteView.as_view(), name='serviceorder_delete'),
    path('service-orders/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='serviceorder_changelog', kwargs={'model': ServiceOrder}),
    path('service-orders/<int:pk>/journal/', ObjectJournalView.as_view(), name='serviceorder_journal', kwargs={'model': ServiceOrder}),
    path('service-orders/delete/', views.ServiceOrderBulkDeleteView.as_view(), name='serviceorder_bulk_delete'),
    
    # =============================================================================
    # TaskDetail 路由
    # =============================================================================
    path('tasks/', views.TaskDetailListView.as_view(), name='taskdetail_list'),
    path('tasks/add/', views.TaskDetailEditView.as_view(), name='taskdetail_add'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='taskdetail'),
    path('tasks/<int:pk>/edit/', views.TaskDetailEditView.as_view(), name='taskdetail_edit'),
    path('tasks/<int:pk>/delete/', views.TaskDetailDeleteView.as_view(), name='taskdetail_delete'),
    path('tasks/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='taskdetail_changelog', kwargs={'model': TaskDetail}),
    path('tasks/<int:pk>/journal/', ObjectJournalView.as_view(), name='taskdetail_journal', kwargs={'model': TaskDetail}),
    path('tasks/delete/', views.TaskDetailBulkDeleteView.as_view(), name='taskdetail_bulk_delete'),
    
    # =============================================================================
    # ResourceLedger 路由
    # =============================================================================
    path('resources/', views.ResourceLedgerListView.as_view(), name='resourceledger_list'),
    path('resources/add/', views.ResourceLedgerEditView.as_view(), name='resourceledger_add'),
    path('resources/<int:pk>/', views.ResourceLedgerView.as_view(), name='resourceledger'),
    path('resources/<int:pk>/edit/', views.ResourceLedgerEditView.as_view(), name='resourceledger_edit'),
    path('resources/<int:pk>/delete/', views.ResourceLedgerDeleteView.as_view(), name='resourceledger_delete'),
    path('resources/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='resourceledger_changelog', kwargs={'model': ResourceLedger}),
    path('resources/<int:pk>/journal/', ObjectJournalView.as_view(), name='resourceledger_journal', kwargs={'model': ResourceLedger}),
    path('resources/delete/', views.ResourceLedgerBulkDeleteView.as_view(), name='resourceledger_bulk_delete'),
]

from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.index, name='index'),
    path('action/', views.action_selection, name='action_selection'),
    path('clock/<int:user_id>/<str:action>/', views.clock_action, name='clock_action'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clear/', views.clear_session, name='clear_session'),
    path('reports/', views.reports, name='reports'),
    path('reports/export/csv/', views.report_export_csv, name='report_export_csv'),
    path('reports/export/pdf/', views.report_export_pdf, name='report_export_pdf'),
]

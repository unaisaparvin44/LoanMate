from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('admin/', views.admin_reports, name='admin_reports'),
    path('admin/export/', views.export_admin_csv, name='export_admin_csv'),
    path('officer/', views.officer_reports, name='officer_reports'),
    path('officer/export/', views.export_officer_csv, name='export_officer_csv'),
]

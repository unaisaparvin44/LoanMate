from django.contrib import admin
from django.urls import path, include
from loanmate.dashboard_views import (
    admin_dashboard,
    user_dashboard,
    officer_dashboard
)
from loanmate.admin_views import (
    admin_dashboard_view,
    admin_users_list,
    admin_officers_list,
    admin_loan_applications_list,
    admin_loan_application_detail,
    admin_loan_types_list,
    admin_loan_type_create,
    admin_loan_type_edit,
    admin_loan_type_toggle,
    admin_user_toggle_active,
)
from django.views.generic import TemplateView

urlpatterns = [
    # Django Super Admin (developer only - DO NOT MODIFY)
    path('admin/', admin.site.urls),

    # Documentation
    path('docs/database/', TemplateView.as_view(template_name='documentation/database_tables.html'), name='db_docs'),

    # Custom Admin Dashboard (faculty-facing)
    path('custom-admin/', admin_dashboard_view, name='admin_dashboard'),
    path('custom-admin/users/', admin_users_list, name='admin_users'),
    path('custom-admin/users/toggle/<int:user_id>/', admin_user_toggle_active, name='admin_user_toggle'),
    path('custom-admin/officers/', admin_officers_list, name='admin_officers'),
    path('custom-admin/loan-applications/', admin_loan_applications_list, name='admin_loan_applications'),
    path('custom-admin/loan-applications/<int:application_id>/', admin_loan_application_detail, name='admin_loan_application_detail'),
    path('custom-admin/loan-types/', admin_loan_types_list, name='admin_loan_types'),
    path('custom-admin/loan-types/create/', admin_loan_type_create, name='admin_loan_type_create'),
    path('custom-admin/loan-types/edit/<int:loan_type_id>/', admin_loan_type_edit, name='admin_loan_type_edit'),
    path('custom-admin/loan-types/toggle/<int:loan_type_id>/', admin_loan_type_toggle, name='admin_loan_type_toggle'),

    # User and Officer Dashboards (existing - DO NOT MODIFY)
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('officer/dashboard/', officer_dashboard, name='officer_dashboard'),

    # App URLs (existing - DO NOT MODIFY)
    path('loans/', include('loans.urls')),
    path('officer/', include('officers.urls')),
    path('reports/', include('reports.urls')),
    path('ml/', include('ml_engine.urls')),
    path('', include('accounts.urls')),
]


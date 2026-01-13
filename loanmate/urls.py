from django.contrib import admin
from django.urls import path, include
from loanmate.dashboard_views import (
    admin_dashboard,
    user_dashboard,
    officer_dashboard
)

urlpatterns = [
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),

    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('officer/dashboard/', officer_dashboard, name='officer_dashboard'),

    path('loans/', include('loans.urls')),
    path('officer/', include('officers.urls')),
    path('', include('accounts.urls')),
]

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@role_required('user')
def user_dashboard(request):
    return render(request, 'dashboards/user_dashboard.html')

@role_required('officer')
def officer_dashboard(request):
    return render(request, 'dashboards/officer_dashboard.html')

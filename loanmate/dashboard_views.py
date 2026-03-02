from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@role_required('user')
def user_dashboard(request):
    from loans.models import LoanApplication
    from django.db.models import Q
    
    # Get recent applications for notifications (last 3, prioritizing reviewed ones)
    recent_applications = LoanApplication.objects.filter(
        user=request.user
    ).order_by('-reviewed_at', '-created_at')[:3]
    
    context = {
        'recent_applications': recent_applications,
    }
    
    return render(request, 'dashboards/user_dashboard.html', context)

@role_required('officer')
def officer_dashboard(request):
    return render(request, 'dashboards/officer_dashboard.html')

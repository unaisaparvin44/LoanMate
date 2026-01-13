from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from accounts.decorators import role_required
from loans.models import LoanApplication


@role_required("officer")
def officer_application_list(request):
    """Display all pending loan applications"""
    pending_applications = LoanApplication.objects.filter(
        status='PENDING'
    ).order_by('-created_at')
    
    context = {
        'applications': pending_applications
    }
    return render(request, 'officers/application_list.html', context)


@role_required("officer")
def officer_application_detail(request, pk):
    """Display application details and handle review submission"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    if request.method == 'POST':
        # Handle review submission
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        # Validate status
        if status in ['APPROVED', 'REJECTED']:
            application.status = status
            application.remarks = remarks
            application.reviewed_at = timezone.now()
            application.save()
            
            return redirect('officers:application_list')
    
    context = {
        'application': application
    }
    return render(request, 'officers/application_detail.html', context)


@role_required("officer")
def officer_application_all(request):
    """Display all loan applications with optional status filter"""
    status_filter = request.GET.get('status', 'ALL')
    
    # Start with all applications
    applications = LoanApplication.objects.all()
    
    # Apply filter if status is not ALL
    if status_filter in ['PENDING', 'APPROVED', 'REJECTED']:
        applications = applications.filter(status=status_filter)
    
    # Order by created_at descending
    applications = applications.order_by('-created_at')
    
    context = {
        'applications': applications,
        'current_filter': status_filter
    }
    return render(request, 'officers/application_all.html', context)

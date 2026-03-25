from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from accounts.decorators import role_required
from loans.models import LoanApplication
from ml_engine.predictor import predict as ml_predict


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
            application.reviewed_by = request.user
            application.save()
            
            return redirect('officers:application_list')
    
    context = {
        'application': application,
        'ml_prediction': ml_predict(application),
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


from django.contrib import messages

@role_required("officer")
def officer_profile(request):
    """View and edit officer profile details"""
    profile = request.user.userprofile
    
    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        designation = request.POST.get('designation', '').strip()
        experience_str = request.POST.get('experience', '').strip()
        
        errors = []
        
        # Validation
        if phone:
            if not phone.isdigit():
                errors.append("Phone number must contain only numbers.")
            elif len(phone) < 10 or len(phone) > 15:
                errors.append("Phone number must be between 10 and 15 digits.")
                
        experience = None
        if experience_str:
            try:
                experience = int(experience_str)
                if experience < 0:
                    errors.append("Experience must be a positive number.")
            except ValueError:
                errors.append("Experience must be a valid number.")
                
        if not errors:
            profile.phone_number = phone or None
            profile.address = address or None
            profile.designation = designation or None
            profile.experience = experience if experience_str else None
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('officers:officer_profile')
        else:
            for error in errors:
                messages.error(request, error)
                
    context = {
        'profile': profile
    }
    return render(request, 'officers/officer_profile.html', context)


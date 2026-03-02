from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from accounts.decorators import staff_required
from accounts.models import UserProfile
from loans.models import LoanApplication, LoanType


@staff_required
def admin_dashboard_view(request):
    """
    Custom Admin Dashboard - Overview with statistics
    """
    # Calculate statistics
    total_users = User.objects.filter(userprofile__role='user').count()
    total_officers = User.objects.filter(userprofile__role='officer').count()
    total_applications = LoanApplication.objects.count()
    
    # Status breakdown
    pending_count = LoanApplication.objects.filter(status='PENDING').count()
    approved_count = LoanApplication.objects.filter(status='APPROVED').count()
    rejected_count = LoanApplication.objects.filter(status='REJECTED').count()
    
    # Active loan types
    active_loan_types = LoanType.objects.filter(is_active=True).count()
    
    # Recent applications (last 5)
    recent_applications = LoanApplication.objects.select_related(
        'user', 'loan_type'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_officers': total_officers,
        'total_applications': total_applications,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'active_loan_types': active_loan_types,
        'recent_applications': recent_applications,
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)


@staff_required
def admin_users_list(request):
    """
    List all users (read-only)
    """
    # Get search query
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '').strip()
    
    # Base queryset
    users = User.objects.select_related('userprofile').all()
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply role filter
    if role_filter:
        users = users.filter(userprofile__role=role_filter)
    
    # Order by date joined (newest first)
    users = users.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
    }
    
    return render(request, 'dashboards/admin_users_list.html', context)


@staff_required
def admin_officers_list(request):
    """
    List all officers with their statistics
    """
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Base queryset - only officers
    officers = User.objects.filter(
        userprofile__role='officer'
    ).select_related('userprofile')
    
    # Apply search filter
    if search_query:
        officers = officers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Annotate with loan counts
    officers = officers.annotate(
        total_reviewed=Count('loanapplication', filter=Q(loanapplication__reviewed_at__isnull=False)),
        pending_assigned=Count('loanapplication', filter=Q(loanapplication__status='PENDING'))
    )
    
    # Order by date joined (newest first)
    officers = officers.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(officers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'dashboards/admin_officers_list.html', context)


@staff_required
def admin_loan_applications_list(request):
    """
    List all loan applications with filtering
    """
    # Get filter parameters
    status_filter = request.GET.get('status', '').strip()
    loan_type_filter = request.GET.get('loan_type', '').strip()
    search_query = request.GET.get('search', '').strip()
    
    # Base queryset
    applications = LoanApplication.objects.select_related(
        'user', 'loan_type'
    ).all()
    
    # Apply status filter
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Apply loan type filter
    if loan_type_filter:
        applications = applications.filter(loan_type_id=loan_type_filter)
    
    # Apply search filter (by username)
    if search_query:
        applications = applications.filter(
            user__username__icontains=search_query
        )
    
    # Order by created date (newest first)
    applications = applications.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all loan types for filter dropdown
    loan_types = LoanType.objects.all()
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'loan_type_filter': loan_type_filter,
        'search_query': search_query,
        'loan_types': loan_types,
    }
    
    return render(request, 'dashboards/admin_loan_applications.html', context)


@staff_required
def admin_loan_application_detail(request, application_id):
    """
    View detailed information about a specific loan application (read-only)
    """
    application = get_object_or_404(
        LoanApplication.objects.select_related('user', 'loan_type'),
        id=application_id
    )
    
    context = {
        'application': application,
    }
    
    return render(request, 'dashboards/admin_loan_application_detail.html', context)


@staff_required
def admin_loan_types_list(request):
    """
    List and manage loan types
    """
    loan_types = LoanType.objects.all().order_by('name')
    
    context = {
        'loan_types': loan_types,
    }
    
    return render(request, 'dashboards/admin_loan_types.html', context)


@staff_required
def admin_loan_type_create(request):
    """
    Create a new loan type
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            LoanType.objects.create(
                name=name,
                description=description,
                is_active=is_active
            )
            return redirect('admin_loan_types')
    
    return render(request, 'dashboards/admin_loan_type_form.html', {
        'action': 'Create',
    })


@staff_required
def admin_loan_type_edit(request, loan_type_id):
    """
    Edit an existing loan type
    """
    loan_type = get_object_or_404(LoanType, id=loan_type_id)
    
    if request.method == 'POST':
        loan_type.name = request.POST.get('name', '').strip()
        loan_type.description = request.POST.get('description', '').strip()
        loan_type.is_active = request.POST.get('is_active') == 'on'
        loan_type.save()
        return redirect('admin_loan_types')
    
    context = {
        'loan_type': loan_type,
        'action': 'Edit',
    }
    
    return render(request, 'dashboards/admin_loan_type_form.html', context)


@staff_required
def admin_loan_type_toggle(request, loan_type_id):
    """
    Toggle is_active status for a loan type (AJAX)
    """
    if request.method == 'POST':
        loan_type = get_object_or_404(LoanType, id=loan_type_id)
        loan_type.is_active = not loan_type.is_active
        loan_type.save()
        
        return JsonResponse({
            'success': True,
            'is_active': loan_type.is_active
        })
    
    return JsonResponse({'success': False}, status=400)


@staff_required
def admin_user_toggle_active(request, user_id):
    """
    Toggle is_active status for a user (AJAX)
    """
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active
        })
    
    return JsonResponse({'success': False}, status=400)

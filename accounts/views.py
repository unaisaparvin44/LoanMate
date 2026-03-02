from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')
    return redirect('accounts:login')

@login_required
def role_redirect(request):
    user = request.user

    if user.is_superuser or user.is_staff:
        return redirect('admin_dashboard')

    if hasattr(user, 'userprofile'):
        if user.userprofile.role == 'user':
            return redirect('user_dashboard')
        elif user.userprofile.role == 'officer':
            return redirect('officer_dashboard')

    return redirect('accounts:login')
    return redirect('accounts:login')

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'user')  # Default to user if distinct choice fails

        # Validation
        errors = []
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken.")
        
        if password != confirm_password:
            errors.append("Passwords do not match.")
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if errors:
            return render(request, 'accounts/register.html', {
                'errors': errors,
                'data': request.POST  # Preserve inputs
            })

        # Create User
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Create UserProfile
            # Check if UserProfile exists (signal might create it, though typically manual here)
            # Assuming manual creation is needed based on previous context or signals
            # Retrieve auto-created UserProfile (from signals) and update role
            profile = user.userprofile
            profile.role = role
            profile.save()
            
            return redirect('accounts:login')
        except Exception as e:
            errors.append(f"Registration failed: {str(e)}")
            return render(request, 'accounts/register.html', {
                'errors': errors, 
                'data': request.POST
            })

    return render(request, 'accounts/register.html')

from accounts.decorators import role_required
from django.contrib import messages

@role_required("user")
def profile_view(request):
    """View user profile with loan statistics"""
    profile = request.user.userprofile
    
    # Import LoanApplication here to avoid circular imports
    from loans.models import LoanApplication
    
    # Calculate loan statistics
    total_loans = LoanApplication.objects.filter(user=request.user).count()
    approved_loans = LoanApplication.objects.filter(user=request.user, status='APPROVED').count()
    rejected_loans = LoanApplication.objects.filter(user=request.user, status='REJECTED').count()
    
    context = {
        'profile': profile,
        'total_loans': total_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
    }
    
    return render(request, 'accounts/profile_view.html', context)

@role_required("user")
def profile_edit(request):
    """Edit user profile"""
    profile = request.user.userprofile
    
    if request.method == 'POST':
        # Get form data
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        employment_type = request.POST.get('employment_type', '').strip()
        monthly_income = request.POST.get('monthly_income', '').strip()
        
        # Validation
        errors = []
        
        # Validate monthly income if provided
        if monthly_income:
            try:
                income_value = int(monthly_income)
                if income_value < 0:
                    errors.append("Monthly income cannot be negative.")
            except ValueError:
                errors.append("Monthly income must be a valid number.")
        
        if errors:
            return render(request, 'accounts/profile_edit.html', {
                'profile': profile,
                'errors': errors,
                'data': request.POST
            })
        
        # Update profile
        profile.phone_number = phone_number if phone_number else None
        profile.address = address if address else None
        profile.employment_type = employment_type if employment_type else None
        profile.monthly_income = int(monthly_income) if monthly_income else None
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile_view')
    
    return render(request, 'accounts/profile_edit.html', {'profile': profile})


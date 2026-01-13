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

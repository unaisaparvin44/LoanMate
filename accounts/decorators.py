from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def role_required(role_name):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not hasattr(user, 'userprofile'):
                return redirect('accounts:login')

            if user.userprofile.role != role_name:
                return redirect('accounts:login')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def staff_required(view_func):
    """
    Decorator to restrict access to staff users only.
    Used for Custom Admin dashboard access.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Access denied. Staff privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


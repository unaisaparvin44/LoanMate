from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

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

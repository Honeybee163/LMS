from django.http import HttpResponseForbidden
from functools import wraps

def role_required(roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'member_profile'):
                user_role = request.user.member_profile.role
                if user_role in roles:
                    return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("You are not allowed!")
        return wrapper
    return decorator
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'{reverse("account_login")}?next={request.get_full_path()}')
        if not request.user.groups.filter(name='Admin').exists():
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def author_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'{reverse("account_login")}?next={request.get_full_path()}')
        if not (request.user.groups.filter(name='Admin').exists() or
                request.user.groups.filter(name='Author').exists()):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(*role_names):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f'{reverse("account_login")}?next={request.get_full_path()}')
            if not request.user.groups.filter(name__in=role_names).exists():
                return redirect('index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

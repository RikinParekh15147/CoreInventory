"""
Custom permission decorator and utilities for access control.
"""

from functools import wraps
from django.http import HttpResponseForbidden
from apps.access.models import RolePermission


def has_user_permission(user, codename):
    """Check if a user has a specific permission via their role."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not hasattr(user, 'role') or user.role is None:
        return False
    return RolePermission.objects.filter(
        role=user.role,
        permission__codename=codename,
        granted=True,
    ).exists()


def require_permission(codename):
    """
    View decorator that checks custom permission.
    Usage: @require_permission('can_validate_receipt')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_user_permission(request.user, codename):
                return HttpResponseForbidden(
                    'You do not have permission to perform this action.'
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

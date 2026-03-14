from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden


class AdminPanelAccessMiddleware(MiddlewareMixin):
    """Restrict /admin-panel/ to Admin role users or superusers."""

    def process_request(self, request):
        if not request.path.startswith('/admin-panel/'):
            return None

        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('account_login')

        if request.user.is_superuser:
            return None

        if hasattr(request.user, 'role') and request.user.role:
            if request.user.role.name == 'Admin':
                return None

        return HttpResponseForbidden('Access denied. Admin role required.')

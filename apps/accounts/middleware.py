from django.shortcuts import redirect
from django.urls import reverse

class ApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user is approved
            # Skip check for admins/superusers if we want, but usually better to have them approved too
            # or just skip for is_superuser.
            if not request.user.is_approved and not request.user.is_superuser:
                allowed_paths = [
                    reverse('accounts:pending_approval'),
                    reverse('account_logout'),
                ]
                # Also allow static files and media if needed, but middleware usually handles this
                if request.path not in allowed_paths and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                    return redirect('accounts:pending_approval')
        
        response = self.get_response(request)
        return response

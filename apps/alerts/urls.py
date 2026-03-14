from django.urls import path
from django.http import JsonResponse
from apps.alerts.models import Notification

app_name = 'alerts'


def notification_count(request):
    """Return unread notification count for HTMX badge."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(is_read=False).count()
    else:
        count = 0
    return JsonResponse({'count': count})


urlpatterns = [
    path('count/', notification_count, name='count'),
]

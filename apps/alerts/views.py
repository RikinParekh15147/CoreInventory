"""
Alerts views — notification list and count.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    qs = Notification.objects.select_related('product', 'location').order_by('-created_at')
    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get('page'))
    # Mark all visible as read
    unread_ids = [n.pk for n in page_obj if not n.is_read]
    if unread_ids:
        Notification.objects.filter(pk__in=unread_ids).update(is_read=True)
    return render(request, 'alerts/list.html', {'page_obj': page_obj})


@login_required
def notification_count(request):
    """Return unread notification count for HTMX badge."""
    count = Notification.objects.filter(is_read=False).count()

    if hasattr(request, 'htmx') and request.htmx:
        return render(request, 'alerts/partials/badge.html', {'count': count})

    return JsonResponse({'count': count})

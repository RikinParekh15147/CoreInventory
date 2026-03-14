"""
Root URL configuration for CoreInventory.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect


def health_check(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('', lambda r: redirect('/dashboard/'), name='root'),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('products/', include('apps.products.urls')),
    path('receipts/', include('apps.receipts.urls')),
    path('deliveries/', include('apps.deliveries.urls')),
    path('transfers/', include('apps.transfers.urls')),
    path('adjustments/', include('apps.adjustments.urls')),
    path('ledger/', include('apps.ledger.urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('admin-panel/', include('apps.access.urls')),
    path('settings/', include('apps.warehouses.urls')),
]

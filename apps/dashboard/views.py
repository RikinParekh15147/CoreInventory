"""
Dashboard views.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q, Sum, Value, DecimalField
from apps.products.models import Product
from apps.receipts.models import Receipt
from apps.deliveries.models import Delivery
from apps.ledger.models import StockMove, Stock
from apps.alerts.models import Notification
from apps.chat.services import generate_user_insights
from django.views.decorators.http import require_POST
from django.db.models.functions import Coalesce


@login_required
def dashboard_view(request):
    """Main dashboard with KPIs and recent activity."""
    total_products = Product.objects.filter(is_active=True).count()

    # Low stock and out of stock — aggregate by product
    products_with_stock = Product.objects.filter(is_active=True).annotate(
        total_qty=Coalesce(Sum('stock_records__quantity'), Value(0, output_field=DecimalField()))
    )

    low_stock_count = 0
    out_of_stock_count = 0
    for product in products_with_stock:
        if product.total_qty <= 0:
            out_of_stock_count += 1
        elif product.total_qty <= product.reorder_point:
            low_stock_count += 1

    pending_receipts = Receipt.objects.filter(
        status__in=['draft', 'waiting', 'ready']
    ).count()

    pending_deliveries = Delivery.objects.filter(
        status__in=['draft', 'waiting', 'ready']
    ).count()

    recent_moves = StockMove.objects.select_related(
        'product', 'from_location', 'to_location', 'created_by'
    ).order_by('-created_at')[:15]

    # Fetch existing AI insights for the user
    ai_insights = Notification.objects.filter(
        user=request.user, 
        type='ai_insight'
    ).order_by('-created_at')

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
        'recent_moves': recent_moves,
        'ai_insights': ai_insights,
    }

    # Return partial for HTMX requests
    if hasattr(request, 'htmx') and request.htmx:
        return render(request, 'dashboard/partials/kpis.html', context)

    return render(request, 'dashboard/index.html', context)


@login_required
def kpis_partial(request):
    """HTMX partial endpoint for refreshing KPI cards."""
    return dashboard_view(request)


@login_required
@require_POST
def generate_ai_insights(request):
    """HTMX endpoint to trigger AI insight generation."""
    result = generate_user_insights(request.user)
    
    insights = Notification.objects.filter(
        user=request.user, 
        type='ai_insight'
    ).order_by('-created_at')
    
    return render(request, 'dashboard/partials/ai_insights_content.html', {
        'ai_insights': insights,
        'ai_error': result.get('message') if not result.get('success') else None,
    })

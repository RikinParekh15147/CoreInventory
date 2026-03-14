"""
Dashboard views.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q, Sum
from apps.products.models import Product
from apps.receipts.models import Receipt
from apps.deliveries.models import Delivery
from apps.ledger.models import StockMove, Stock


@login_required
def dashboard_view(request):
    """Main dashboard with KPIs and recent activity."""
    total_products = Product.objects.filter(is_active=True).count()

    # Low stock and out of stock — aggregate by product
    stock_totals = (
        Stock.objects.filter(product__is_active=True)
        .values('product')
        .annotate(total_qty=Sum('quantity'))
    )

    low_stock_count = 0
    out_of_stock_count = 0
    for entry in stock_totals:
        product = Product.objects.get(pk=entry['product'])
        if entry['total_qty'] <= 0:
            out_of_stock_count += 1
        elif entry['total_qty'] <= product.reorder_point:
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

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
        'recent_moves': recent_moves,
    }

    # Return partial for HTMX requests
    if hasattr(request, 'htmx') and request.htmx:
        return render(request, 'dashboard/partials/kpis.html', context)

    return render(request, 'dashboard/index.html', context)


@login_required
def kpis_partial(request):
    """HTMX partial endpoint for refreshing KPI cards."""
    return dashboard_view(request)

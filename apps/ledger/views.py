"""
Ledger views — read-only stock move history.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import StockMove


@login_required
def move_list(request):
    qs = StockMove.objects.select_related('product', 'from_location', 'to_location').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q) |
            Q(product__sku__icontains=q) |
            Q(reference_ref__icontains=q)
        )
    move_type = request.GET.get('type')
    if move_type:
        qs = qs.filter(move_type=move_type)
    paginator = Paginator(qs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'ledger/move_list.html', {
        'page_obj': page_obj, 'q': q, 'type_filter': move_type,
    })

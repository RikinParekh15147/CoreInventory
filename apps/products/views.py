"""
Product views — list, detail, create, edit.
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.functions import Coalesce

from .models import Product, ProductCategory
from .forms import ProductForm
from apps.ledger.models import Stock


@login_required
def product_list(request):
    """Paginated product list with search and category filter."""
    qs = Product.objects.select_related('category', 'unit').annotate(
        annotated_stock=Coalesce(
            Sum('stock_records__quantity'),
            Value(0, output_field=DecimalField()),
            output_field=DecimalField(),
        ),
    )

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Active filter
    active_filter = request.GET.get('active', 'all')
    if active_filter == 'yes':
        qs = qs.filter(is_active=True)
    elif active_filter == 'no':
        qs = qs.filter(is_active=False)

    # Stock status filter
    stock_status = request.GET.get('stock_status')
    if stock_status == 'low':
        qs = qs.filter(annotated_stock__gt=0, annotated_stock__lte=models.F('reorder_point'))
    elif stock_status == 'out':
        qs = qs.filter(annotated_stock__lte=0)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    categories = ProductCategory.objects.all()

    return render(request, 'products/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'q': q,
        'category_id': category_id,
        'active_filter': active_filter,
    })


@login_required
def product_detail(request, pk):
    """Product detail with stock breakdown by location."""
    product = get_object_or_404(Product.objects.select_related('category', 'unit'), pk=pk)
    stock_records = Stock.objects.filter(product=product).select_related('location', 'location__warehouse')

    return render(request, 'products/detail.html', {
        'product': product,
        'stock_records': stock_records,
    })


@login_required
def product_create(request):
    """Create a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('products:detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'products/form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def product_edit(request, pk):
    """Edit an existing product."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('products:detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/form.html', {
        'form': form,
        'product': product,
        'is_edit': True,
    })

"""
Receipt views — list, detail, create, edit, status change, validate.
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Receipt
from .forms import ReceiptForm, ReceiptLineFormSet
from .services import validate_receipt
from apps.access.decorators import require_permission


@login_required
def receipt_list(request):
    qs = Receipt.objects.select_related('destination', 'created_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(ref__icontains=q) | Q(supplier_name__icontains=q))
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'receipts/list.html', {
        'page_obj': page_obj, 'q': q, 'status_filter': status,
    })


@login_required
def receipt_detail(request, pk):
    receipt = get_object_or_404(
        Receipt.objects.select_related('destination', 'created_by', 'validated_by'),
        pk=pk,
    )
    lines = receipt.lines.select_related('product', 'unit')
    return render(request, 'receipts/detail.html', {
        'receipt': receipt, 'lines': lines,
    })


@login_required
@require_permission('can_create_receipt')
def receipt_create(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        formset = ReceiptLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            receipt = form.save(commit=False)
            receipt.created_by = request.user
            receipt.save()
            formset.instance = receipt
            formset.save()
            messages.success(request, f'Receipt {receipt.ref} created.')
            return redirect('receipts:detail', pk=receipt.pk)
    else:
        form = ReceiptForm()
        formset = ReceiptLineFormSet()
    return render(request, 'receipts/form.html', {
        'form': form, 'formset': formset, 'is_edit': False,
    })


@login_required
def receipt_edit(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    if receipt.status == 'done':
        messages.error(request, 'Cannot edit a completed receipt.')
        return redirect('receipts:detail', pk=pk)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt)
        formset = ReceiptLineFormSet(request.POST, instance=receipt)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Receipt {receipt.ref} updated.')
            return redirect('receipts:detail', pk=receipt.pk)
    else:
        form = ReceiptForm(instance=receipt)
        formset = ReceiptLineFormSet(instance=receipt)
    return render(request, 'receipts/form.html', {
        'form': form, 'formset': formset, 'receipt': receipt, 'is_edit': True,
    })


@login_required
@require_permission('can_validate_receipt')
def receipt_change_status(request, pk):
    """Change receipt status (POST only)."""
    receipt = get_object_or_404(Receipt, pk=pk)
    new_status = request.POST.get('status')
    valid_transitions = {
        'draft': ['waiting', 'cancelled'],
        'waiting': ['ready', 'cancelled'],
        'ready': ['done', 'cancelled'],
    }
    allowed = valid_transitions.get(receipt.status, [])

    if new_status == 'done':
        try:
            validate_receipt(receipt, request.user)
            messages.success(request, f'Receipt {receipt.ref} validated and completed.')
        except ValueError as e:
            messages.error(request, str(e))
    elif new_status in allowed:
        receipt.status = new_status
        receipt.save()
        messages.success(request, f'Receipt {receipt.ref} status changed to {new_status}.')
    else:
        messages.error(request, f'Cannot change status from {receipt.status} to {new_status}.')

    return redirect('receipts:detail', pk=pk)

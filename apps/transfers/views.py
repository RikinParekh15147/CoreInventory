"""
Transfer views.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Transfer
from .forms import TransferForm, TransferLineFormSet
from .services import validate_transfer
from apps.access.decorators import require_permission


@login_required
def transfer_list(request):
    qs = Transfer.objects.select_related('from_location', 'to_location', 'created_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(ref__icontains=q))
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'transfers/list.html', {'page_obj': page_obj, 'q': q, 'status_filter': status})


@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(Transfer.objects.select_related('from_location', 'to_location', 'created_by', 'validated_by'), pk=pk)
    lines = transfer.lines.select_related('product', 'unit')
    return render(request, 'transfers/detail.html', {'transfer': transfer, 'lines': lines})


@login_required
@require_permission('can_create_transfer')
def transfer_create(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        formset = TransferLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user
            transfer.save()
            formset.instance = transfer
            formset.save()
            messages.success(request, f'Transfer {transfer.ref} created.')
            return redirect('transfers:detail', pk=transfer.pk)
    else:
        form = TransferForm()
        formset = TransferLineFormSet()
    return render(request, 'transfers/form.html', {'form': form, 'formset': formset, 'is_edit': False})


@login_required
def transfer_edit(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    if transfer.status == 'done':
        messages.error(request, 'Cannot edit a completed transfer.')
        return redirect('transfers:detail', pk=pk)
    if request.method == 'POST':
        form = TransferForm(request.POST, instance=transfer)
        formset = TransferLineFormSet(request.POST, instance=transfer)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Transfer {transfer.ref} updated.')
            return redirect('transfers:detail', pk=transfer.pk)
    else:
        form = TransferForm(instance=transfer)
        formset = TransferLineFormSet(instance=transfer)
    return render(request, 'transfers/form.html', {'form': form, 'formset': formset, 'transfer': transfer, 'is_edit': True})


@login_required
@require_permission('can_validate_transfer')
def transfer_change_status(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    new_status = request.POST.get('status')
    valid_transitions = {'draft': ['waiting', 'cancelled'], 'waiting': ['ready', 'cancelled'], 'ready': ['done', 'cancelled']}
    allowed = valid_transitions.get(transfer.status, [])
    if new_status == 'done':
        try:
            validate_transfer(transfer, request.user)
            messages.success(request, f'Transfer {transfer.ref} validated and completed.')
        except (ValueError, Exception) as e:
            messages.error(request, str(e))
    elif new_status in allowed:
        transfer.status = new_status
        transfer.save()
        messages.success(request, f'Transfer {transfer.ref} status changed to {new_status}.')
    else:
        messages.error(request, f'Cannot change status from {transfer.status} to {new_status}.')
    return redirect('transfers:detail', pk=pk)

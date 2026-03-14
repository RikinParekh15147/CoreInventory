"""
Adjustment views.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Adjustment
from .forms import AdjustmentForm, AdjustmentLineFormSet
from .services import validate_adjustment
from apps.access.decorators import require_permission


@login_required
def adjustment_list(request):
    qs = Adjustment.objects.select_related('location', 'created_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(ref__icontains=q))
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'adjustments/list.html', {'page_obj': page_obj, 'q': q, 'status_filter': status})


@login_required
def adjustment_detail(request, pk):
    adjustment = get_object_or_404(Adjustment.objects.select_related('location', 'created_by', 'validated_by'), pk=pk)
    lines = adjustment.lines.select_related('product', 'unit')
    return render(request, 'adjustments/detail.html', {'adjustment': adjustment, 'lines': lines})


@login_required
@require_permission('can_create_adjustment')
def adjustment_create(request):
    if request.method == 'POST':
        form = AdjustmentForm(request.POST)
        formset = AdjustmentLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            adjustment = form.save(commit=False)
            adjustment.created_by = request.user
            adjustment.save()
            formset.instance = adjustment
            formset.save()
            messages.success(request, f'Adjustment {adjustment.ref} created.')
            return redirect('adjustments:detail', pk=adjustment.pk)
    else:
        form = AdjustmentForm()
        formset = AdjustmentLineFormSet()
    return render(request, 'adjustments/form.html', {'form': form, 'formset': formset, 'is_edit': False})


@login_required
def adjustment_edit(request, pk):
    adjustment = get_object_or_404(Adjustment, pk=pk)
    if adjustment.status == 'done':
        messages.error(request, 'Cannot edit a completed adjustment.')
        return redirect('adjustments:detail', pk=pk)
    if request.method == 'POST':
        form = AdjustmentForm(request.POST, instance=adjustment)
        formset = AdjustmentLineFormSet(request.POST, instance=adjustment)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Adjustment {adjustment.ref} updated.')
            return redirect('adjustments:detail', pk=adjustment.pk)
    else:
        form = AdjustmentForm(instance=adjustment)
        formset = AdjustmentLineFormSet(instance=adjustment)
    return render(request, 'adjustments/form.html', {'form': form, 'formset': formset, 'adjustment': adjustment, 'is_edit': True})


@login_required
@require_permission('can_validate_adjustment')
def adjustment_validate(request, pk):
    adjustment = get_object_or_404(Adjustment, pk=pk)
    if request.method == 'POST':
        try:
            validate_adjustment(adjustment, request.user)
            messages.success(request, f'Adjustment {adjustment.ref} validated.')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('adjustments:detail', pk=pk)

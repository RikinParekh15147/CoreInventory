"""
Delivery views.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Delivery
from .forms import DeliveryForm, DeliveryLineFormSet
from .services import validate_delivery
from apps.access.decorators import require_permission


@login_required
def delivery_list(request):
    qs = Delivery.objects.select_related('source', 'created_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(ref__icontains=q) | Q(customer_name__icontains=q))
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'deliveries/list.html', {'page_obj': page_obj, 'q': q, 'status_filter': status})


@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(Delivery.objects.select_related('source', 'created_by', 'validated_by'), pk=pk)
    lines = delivery.lines.select_related('product', 'unit')
    return render(request, 'deliveries/detail.html', {'delivery': delivery, 'lines': lines})


@login_required
@require_permission('can_create_delivery')
def delivery_create(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        formset = DeliveryLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            delivery = form.save(commit=False)
            delivery.created_by = request.user
            delivery.save()
            formset.instance = delivery
            formset.save()
            messages.success(request, f'Delivery {delivery.ref} created.')
            return redirect('deliveries:detail', pk=delivery.pk)
    else:
        form = DeliveryForm()
        formset = DeliveryLineFormSet()
    return render(request, 'deliveries/form.html', {'form': form, 'formset': formset, 'is_edit': False})


@login_required
def delivery_edit(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if delivery.status == 'done':
        messages.error(request, 'Cannot edit a completed delivery.')
        return redirect('deliveries:detail', pk=pk)
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery)
        formset = DeliveryLineFormSet(request.POST, instance=delivery)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Delivery {delivery.ref} updated.')
            return redirect('deliveries:detail', pk=delivery.pk)
    else:
        form = DeliveryForm(instance=delivery)
        formset = DeliveryLineFormSet(instance=delivery)
    return render(request, 'deliveries/form.html', {'form': form, 'formset': formset, 'delivery': delivery, 'is_edit': True})


@login_required
@require_permission('can_validate_delivery')
def delivery_change_status(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    new_status = request.POST.get('status')
    valid_transitions = {'draft': ['waiting', 'cancelled'], 'waiting': ['ready', 'cancelled'], 'ready': ['done', 'cancelled']}
    allowed = valid_transitions.get(delivery.status, [])
    if new_status == 'done':
        try:
            validate_delivery(delivery, request.user)
            messages.success(request, f'Delivery {delivery.ref} validated and completed.')
        except (ValueError, Exception) as e:
            messages.error(request, str(e))
    elif new_status in allowed:
        delivery.status = new_status
        delivery.save()
        messages.success(request, f'Delivery {delivery.ref} status changed to {new_status}.')
    else:
        messages.error(request, f'Cannot change status from {delivery.status} to {new_status}.')
    return redirect('deliveries:detail', pk=pk)

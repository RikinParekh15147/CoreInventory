"""
Warehouse settings views.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Warehouse, Location


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.prefetch_related('locations')
    return render(request, 'admin_panel/warehouse_list.html', {'warehouses': warehouses})


@login_required
def warehouse_edit(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    locations = warehouse.locations.all()
    if request.method == 'POST':
        warehouse.name = request.POST.get('name', warehouse.name).strip()
        warehouse.address = request.POST.get('address', '').strip()
        warehouse.is_active = 'is_active' in request.POST
        warehouse.save()
        messages.success(request, f'Warehouse "{warehouse.name}" updated.')
        return redirect('warehouses:list')
    return render(request, 'admin_panel/warehouse_edit.html', {
        'warehouse': warehouse, 'locations': locations,
    })

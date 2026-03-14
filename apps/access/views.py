"""
Admin Panel views — user, role, warehouse management.
Restricted to Admin-role users via AdminPanelAccessMiddleware.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.models import CustomUser
from apps.access.models import Role, Permission, RolePermission
from apps.warehouses.models import Warehouse, Location


@login_required
def admin_dashboard(request):
    """Admin panel dashboard — summary of users, roles, warehouses."""
    return render(request, 'admin_panel/dashboard.html', {
        'user_count': CustomUser.objects.count(),
        'role_count': Role.objects.count(),
        'warehouse_count': Warehouse.objects.count(),
        'permission_count': Permission.objects.count(),
    })


# ─── Users ───

@login_required
def user_list(request):
    users = CustomUser.objects.select_related('role', 'warehouse').filter(is_approved=True).order_by('-date_joined')
    pending_users = CustomUser.objects.filter(is_approved=False).count()
    return render(request, 'admin_panel/user_list.html', {
        'users': users,
        'pending_count': pending_users
    })

@login_required
def pending_user_list(request):
    users = CustomUser.objects.select_related('role', 'warehouse').filter(is_approved=False).order_by('-date_joined')
    return render(request, 'admin_panel/pending_user_list.html', {'users': users})

@login_required
def approve_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        role_id = request.POST.get('role')
        if role_id:
            user.role_id = role_id
        user.is_approved = True
        user.save()
        messages.success(request, f'User "{user.email}" has been approved.')
        return redirect('access:pending-user-list')
    
    roles = Role.objects.all()
    return render(request, 'admin_panel/approve_user.html', {'target_user': user, 'roles': roles})


@login_required
def user_edit(request, pk):
    user = get_object_or_404(CustomUser.objects.select_related('role', 'warehouse'), pk=pk)
    roles = Role.objects.all()
    warehouses = Warehouse.objects.filter(is_active=True)

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        role_id = request.POST.get('role')
        warehouse_id = request.POST.get('warehouse')
        user.role_id = role_id if role_id else None
        user.warehouse_id = warehouse_id if warehouse_id else None
        user.is_active = 'is_active' in request.POST
        user.is_approved = 'is_approved' in request.POST
        user.save()
        messages.success(request, f'User "{user.email}" updated.')
        return redirect('access:user-list')

    return render(request, 'admin_panel/user_edit.html', {
        'edit_user': user, 'roles': roles, 'warehouses': warehouses,
    })


# ─── Roles ───

@login_required
def role_list(request):
    roles = Role.objects.prefetch_related('role_permissions__permission').all()
    return render(request, 'admin_panel/role_list.html', {'roles': roles})


@login_required
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    permissions = Permission.objects.all()
    current_perms = set(RolePermission.objects.filter(role=role).values_list('permission_id', flat=True))

    if request.method == 'POST':
        role.name = request.POST.get('name', role.name).strip()
        role.description = request.POST.get('description', '').strip()
        role.save()
        # Sync permissions
        selected_perms = set(map(int, request.POST.getlist('permissions', [])))
        # Remove unselected
        RolePermission.objects.filter(role=role).exclude(permission_id__in=selected_perms).delete()
        # Add new
        for perm_id in selected_perms - current_perms:
            RolePermission.objects.create(role=role, permission_id=perm_id)
        messages.success(request, f'Role "{role.name}" updated.')
        return redirect('access:role-list')

    return render(request, 'admin_panel/role_edit.html', {
        'role': role, 'permissions': permissions, 'current_perms': current_perms,
    })


# ─── Warehouses ───

# Warehouse management moved to apps.warehouses

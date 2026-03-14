"""
Management command to seed all permissions and system roles.
Idempotent — safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from apps.access.models import Role, Permission, RolePermission


PERMISSIONS = [
    # Products
    ('can_view_products', 'Can view products', 'products'),
    ('can_create_product', 'Can create product', 'products'),
    ('can_edit_product', 'Can edit product', 'products'),
    ('can_delete_product', 'Can delete product', 'products'),
    # Receipts
    ('can_view_receipts', 'Can view receipts', 'receipts'),
    ('can_create_receipt', 'Can create receipt', 'receipts'),
    ('can_validate_receipt', 'Can validate receipt', 'receipts'),
    ('can_cancel_receipt', 'Can cancel receipt', 'receipts'),
    # Deliveries
    ('can_view_deliveries', 'Can view deliveries', 'deliveries'),
    ('can_create_delivery', 'Can create delivery', 'deliveries'),
    ('can_validate_delivery', 'Can validate delivery', 'deliveries'),
    ('can_cancel_delivery', 'Can cancel delivery', 'deliveries'),
    # Transfers
    ('can_view_transfers', 'Can view transfers', 'transfers'),
    ('can_create_transfer', 'Can create transfer', 'transfers'),
    ('can_validate_transfer', 'Can validate transfer', 'transfers'),
    # Adjustments
    ('can_view_adjustments', 'Can view adjustments', 'adjustments'),
    ('can_create_adjustment', 'Can create adjustment', 'adjustments'),
    ('can_validate_adjustment', 'Can validate adjustment', 'adjustments'),
    # Warehouses
    ('can_view_warehouses', 'Can view warehouses', 'warehouses'),
    ('can_manage_warehouses', 'Can manage warehouses', 'warehouses'),
    # Reports
    ('can_view_move_history', 'Can view move history', 'reports'),
    ('can_export_data', 'Can export data', 'reports'),
    # Admin
    ('can_access_admin_panel', 'Can access admin panel', 'admin'),
    ('can_manage_users', 'Can manage users', 'admin'),
    ('can_manage_roles', 'Can manage roles', 'admin'),
]

SYSTEM_ROLES = {
    'Admin': [p[0] for p in PERMISSIONS],  # ALL permissions
    'Manager': [
        p[0] for p in PERMISSIONS
        if p[0] not in ('can_manage_users', 'can_manage_roles', 'can_access_admin_panel')
    ],
    'Warehouse Staff': [
        'can_view_products', 'can_view_receipts', 'can_view_deliveries',
        'can_view_transfers', 'can_view_adjustments', 'can_view_warehouses',
        'can_view_move_history',
        'can_create_receipt', 'can_create_delivery', 'can_create_transfer',
    ],
    'Viewer': [
        p[0] for p in PERMISSIONS if p[0].startswith('can_view_')
    ],
}


class Command(BaseCommand):
    help = 'Create all permissions and system roles with default assignments.'

    def handle(self, *args, **options):
        # Create permissions
        for codename, name, module in PERMISSIONS:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name, 'module': module},
            )
            if created:
                self.stdout.write(f'  Created permission: {codename}')
            else:
                self.stdout.write(f'  Permission exists: {codename}')

        # Create system roles and assign permissions
        for role_name, perm_codenames in SYSTEM_ROLES.items():
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={
                    'description': f'System role: {role_name}',
                    'is_system_role': True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created role: {role_name}'))
            else:
                self.stdout.write(f'  Role exists: {role_name}')

            # Assign permissions
            for codename in perm_codenames:
                perm = Permission.objects.get(codename=codename)
                rp, rp_created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                    defaults={'granted': True},
                )
                if rp_created:
                    self.stdout.write(f'    Assigned: {codename} → {role_name}')

        self.stdout.write(self.style.SUCCESS('Done! All permissions and roles seeded.'))

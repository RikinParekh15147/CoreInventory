"""
Management command to seed demo data.
Run create_permissions first.
"""

from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.accounts.models import CustomUser
from apps.access.models import Role
from apps.products.models import ProductCategory, UnitOfMeasure, Product
from apps.warehouses.models import Warehouse, Location
from apps.receipts.models import Receipt, ReceiptLine
from apps.deliveries.models import Delivery, DeliveryLine
from apps.ledger.models import Stock, StockMove


class Command(BaseCommand):
    help = 'Seed demo data: warehouses, users, products, receipts, deliveries, stock.'

    def handle(self, *args, **options):
        # Ensure permissions exist
        call_command('create_permissions')
        self.stdout.write('')

        # ── Roles ─────────────────────────────────────
        admin_role = Role.objects.get(name='Admin')
        manager_role = Role.objects.get(name='Manager')
        staff_role = Role.objects.get(name='Warehouse Staff')
        viewer_role = Role.objects.get(name='Viewer')

        # ── Warehouses ────────────────────────────────
        wh1, _ = Warehouse.objects.get_or_create(
            name='Main Warehouse',
            defaults={'address': '123 Industrial Ave, Mumbai', 'is_active': True},
        )
        wh2, _ = Warehouse.objects.get_or_create(
            name='Secondary Warehouse',
            defaults={'address': '456 Logistics Park, Delhi', 'is_active': True},
        )

        locations = []
        for wh in [wh1, wh2]:
            for loc_name in ['Rack A-1', 'Rack A-2', 'Rack B-1', 'Receiving Bay', 'Shipping Dock']:
                loc, _ = Location.objects.get_or_create(
                    warehouse=wh,
                    name=loc_name,
                    defaults={'is_active': True},
                )
                locations.append(loc)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(locations)} locations'))

        # ── Users ─────────────────────────────────────
        admin_user, created = CustomUser.objects.get_or_create(
            email='admin@coreinventory.com',
            defaults={
                'full_name': 'Admin User',
                'role': admin_role,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  Created admin user'))

        manager_user, created = CustomUser.objects.get_or_create(
            email='manager@coreinventory.com',
            defaults={
                'full_name': 'Manager User',
                'role': manager_role,
                'warehouse': wh1,
            },
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()

        for i, (email, name, wh) in enumerate([
            ('staff1@coreinventory.com', 'Staff One', wh1),
            ('staff2@coreinventory.com', 'Staff Two', wh2),
        ]):
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={'full_name': name, 'role': staff_role, 'warehouse': wh},
            )
            if created:
                user.set_password('staff123')
                user.save()

        viewer_user, created = CustomUser.objects.get_or_create(
            email='viewer@coreinventory.com',
            defaults={'full_name': 'Viewer User', 'role': viewer_role},
        )
        if created:
            viewer_user.set_password('viewer123')
            viewer_user.save()

        self.stdout.write(self.style.SUCCESS('  Created users'))

        # ── Categories & UoM ─────────────────────────
        cat_elec, _ = ProductCategory.objects.get_or_create(name='Electronics')
        cat_office, _ = ProductCategory.objects.get_or_create(name='Office Supplies')
        cat_raw, _ = ProductCategory.objects.get_or_create(name='Raw Materials')

        uom_pcs, _ = UnitOfMeasure.objects.get_or_create(
            name='Pieces', defaults={'abbreviation': 'pcs'})
        uom_kg, _ = UnitOfMeasure.objects.get_or_create(
            name='Kilogram', defaults={'abbreviation': 'kg'})
        uom_l, _ = UnitOfMeasure.objects.get_or_create(
            name='Litre', defaults={'abbreviation': 'L'})

        # ── Products ──────────────────────────────────
        products_data = [
            ('Laptop Dell XPS 15', cat_elec, uom_pcs, 5),
            ('Wireless Mouse', cat_elec, uom_pcs, 20),
            ('USB-C Hub', cat_elec, uom_pcs, 15),
            ('Mechanical Keyboard', cat_elec, uom_pcs, 10),
            ('A4 Paper Ream', cat_office, uom_pcs, 50),
            ('Ballpoint Pens (Box)', cat_office, uom_pcs, 30),
            ('Printer Ink Cartridge', cat_office, uom_pcs, 10),
            ('Steel Sheet 1mm', cat_raw, uom_kg, 100),
            ('Copper Wire 2mm', cat_raw, uom_kg, 50),
            ('Industrial Lubricant', cat_raw, uom_l, 20),
        ]
        products = []
        for name, cat, uom, reorder in products_data:
            prod, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'unit': uom,
                    'reorder_point': Decimal(str(reorder)),
                    'is_active': True,
                },
            )
            products.append(prod)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(products)} products'))

        # ── Initial stock (via receipts) ──────────────
        loc1 = locations[0]  # Main WH, Rack A-1
        for prod in products[:7]:
            Stock.objects.get_or_create(
                product=prod,
                location=loc1,
                defaults={'quantity': Decimal('100')},
            )

        # ── Sample Receipts ───────────────────────────
        today = date.today()
        statuses = ['done', 'done', 'ready', 'draft', 'waiting']
        for i in range(5):
            receipt, created = Receipt.objects.get_or_create(
                ref=f'RCP-{today.year}-{i+1:04d}',
                defaults={
                    'supplier_name': f'Supplier {i+1}',
                    'destination': loc1,
                    'status': statuses[i],
                    'scheduled_date': today - timedelta(days=5-i),
                    'created_by': admin_user,
                },
            )
            if created:
                ReceiptLine.objects.create(
                    receipt=receipt,
                    product=products[i % len(products)],
                    expected_qty=Decimal('50'),
                    received_qty=Decimal('50') if statuses[i] == 'done' else Decimal('0'),
                    unit=products[i % len(products)].unit,
                )

        # ── Sample Deliveries ─────────────────────────
        for i in range(3):
            delivery, created = Delivery.objects.get_or_create(
                ref=f'DLV-{today.year}-{i+1:04d}',
                defaults={
                    'customer_name': f'Customer {i+1}',
                    'source': loc1,
                    'status': ['done', 'ready', 'draft'][i],
                    'scheduled_date': today - timedelta(days=3-i),
                    'created_by': admin_user,
                },
            )
            if created:
                DeliveryLine.objects.create(
                    delivery=delivery,
                    product=products[i],
                    requested_qty=Decimal('10'),
                    delivered_qty=Decimal('10') if i == 0 else Decimal('0'),
                    unit=products[i].unit,
                )

        # ── Sample StockMoves ─────────────────────────
        for i, prod in enumerate(products[:5]):
            StockMove.objects.get_or_create(
                product=prod,
                reference_ref=f'RCP-{today.year}-{i+1:04d}',
                move_type='receipt',
                defaults={
                    'to_location': loc1,
                    'quantity': Decimal('50'),
                    'reference_type': 'Receipt',
                    'reference_id': i + 1,
                    'created_by': admin_user,
                },
            )

        self.stdout.write(self.style.SUCCESS('\nDone! All demo data seeded.'))
        self.stdout.write(self.style.WARNING(
            '\nLogin credentials:\n'
            '  Admin:   admin@coreinventory.com / admin123\n'
            '  Manager: manager@coreinventory.com / manager123\n'
            '  Staff:   staff1@coreinventory.com / staff123\n'
            '  Viewer:  viewer@coreinventory.com / viewer123'
        ))

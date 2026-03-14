"""
Receipt validation service.
All stock mutations are wrapped in transaction.atomic().
"""

from django.db import transaction
from django.utils import timezone
from apps.ledger.models import StockMove, Stock


@transaction.atomic
def validate_receipt(receipt, user):
    """
    Validate a receipt and create stock movements.
    1. Check receipt.status == 'ready'
    2. For each ReceiptLine: create StockMove + upsert Stock
    3. Set status='done', validated_by, validated_at
    4. Trigger async low-stock check
    """
    if receipt.status != 'ready':
        raise ValueError(f'Receipt must be in "ready" status to validate. Current: {receipt.status}')

    for line in receipt.lines.select_related('product', 'unit'):
        # Create stock move
        StockMove.objects.create(
            product=line.product,
            from_location=None,
            to_location=receipt.destination,
            quantity=line.received_qty,
            move_type='receipt',
            reference_type='Receipt',
            reference_id=receipt.pk,
            reference_ref=receipt.ref,
            notes=line.notes,
            created_by=user,
        )

        # Upsert stock
        stock, created = Stock.objects.get_or_create(
            product=line.product,
            location=receipt.destination,
            defaults={'quantity': 0},
        )
        stock.quantity += line.received_qty
        stock.save()

    receipt.status = 'done'
    receipt.validated_by = user
    receipt.validated_at = timezone.now()
    receipt.save()

    # Trigger async low-stock check
    try:
        from apps.alerts.tasks import check_low_stock
        check_low_stock.delay()
    except Exception:
        pass  # Don't fail validation if Celery is unavailable

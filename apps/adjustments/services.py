"""
Adjustment validation service.
"""

from django.db import transaction
from django.utils import timezone
from apps.ledger.models import StockMove, Stock


@transaction.atomic
def validate_adjustment(adjustment, user):
    """
    Validate an adjustment and create stock movements.
    1. For each AdjustmentLine:
       a. diff = actual_qty - recorded_qty
       b. If diff > 0: adjustment_in
       c. If diff < 0: adjustment_out
       d. Set Stock.quantity = actual_qty
    2. Set adjustment.status='done'
    """
    if adjustment.status != 'draft':
        raise ValueError(f'Adjustment must be in "draft" status to validate. Current: {adjustment.status}')

    for line in adjustment.lines.select_related('product', 'unit'):
        diff = line.actual_qty - line.recorded_qty

        if diff > 0:
            StockMove.objects.create(
                product=line.product,
                from_location=None,
                to_location=adjustment.location,
                quantity=diff,
                move_type='adjustment_in',
                reference_type='Adjustment',
                reference_id=adjustment.pk,
                reference_ref=adjustment.ref,
                notes=adjustment.notes,
                created_by=user,
            )
        elif diff < 0:
            StockMove.objects.create(
                product=line.product,
                from_location=adjustment.location,
                to_location=None,
                quantity=abs(diff),
                move_type='adjustment_out',
                reference_type='Adjustment',
                reference_id=adjustment.pk,
                reference_ref=adjustment.ref,
                notes=adjustment.notes,
                created_by=user,
            )

        # Set stock to actual quantity
        stock, created = Stock.objects.get_or_create(
            product=line.product,
            location=adjustment.location,
            defaults={'quantity': 0},
        )
        stock.quantity = line.actual_qty
        stock.save()

    adjustment.status = 'done'
    adjustment.validated_by = user
    adjustment.validated_at = timezone.now()
    adjustment.save()

    # Trigger async low-stock check
    try:
        from apps.alerts.tasks import check_low_stock
        check_low_stock.delay()
    except Exception:
        pass

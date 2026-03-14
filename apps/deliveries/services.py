"""
Delivery validation service.
"""

from django.db import transaction
from django.utils import timezone
from apps.ledger.models import StockMove, Stock


class InsufficientStockError(Exception):
    """Raised when stock is insufficient for a delivery."""
    pass


@transaction.atomic
def validate_delivery(delivery, user):
    """
    Validate a delivery and create stock movements.
    1. Check sufficient stock at source location for each line
    2. If insufficient → raise InsufficientStockError
    3. For each DeliveryLine: create StockMove + decrement Stock
    4. Set status='done'
    """
    if delivery.status != 'ready':
        raise ValueError(f'Delivery must be in "ready" status to validate. Current: {delivery.status}')

    # Pre-check stock availability
    for line in delivery.lines.select_related('product'):
        try:
            stock = Stock.objects.get(
                product=line.product,
                location=delivery.source,
            )
            if stock.quantity < line.delivered_qty:
                raise InsufficientStockError(
                    f'Insufficient stock for {line.product.name} at {delivery.source}. '
                    f'Available: {stock.quantity}, Requested: {line.delivered_qty}'
                )
        except Stock.DoesNotExist:
            raise InsufficientStockError(
                f'No stock found for {line.product.name} at {delivery.source}'
            )

    # Process lines
    for line in delivery.lines.select_related('product', 'unit'):
        StockMove.objects.create(
            product=line.product,
            from_location=delivery.source,
            to_location=None,
            quantity=line.delivered_qty,
            move_type='delivery',
            reference_type='Delivery',
            reference_id=delivery.pk,
            reference_ref=delivery.ref,
            notes=line.notes,
            created_by=user,
        )

        stock = Stock.objects.get(
            product=line.product,
            location=delivery.source,
        )
        stock.quantity -= line.delivered_qty
        stock.save()

    delivery.status = 'done'
    delivery.validated_by = user
    delivery.validated_at = timezone.now()
    delivery.save()

    # Trigger async low-stock check
    try:
        from apps.alerts.tasks import check_low_stock
        check_low_stock.delay()
    except Exception:
        pass

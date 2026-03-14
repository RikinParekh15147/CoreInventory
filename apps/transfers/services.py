"""
Transfer validation service.
"""

from django.db import transaction
from django.utils import timezone
from apps.ledger.models import StockMove, Stock
from apps.deliveries.services import InsufficientStockError


@transaction.atomic
def validate_transfer(transfer, user):
    """
    Validate a transfer and create stock movements.
    1. Check stock at from_location
    2. For each TransferLine: create paired StockMoves + adjust Stock at both locations
    3. Set status='done'
    """
    if transfer.status != 'ready':
        raise ValueError(f'Transfer must be in "ready" status to validate. Current: {transfer.status}')

    # Pre-check stock availability
    for line in transfer.lines.select_related('product'):
        try:
            stock = Stock.objects.get(
                product=line.product,
                location=transfer.from_location,
            )
            if stock.quantity < line.qty:
                raise InsufficientStockError(
                    f'Insufficient stock for {line.product.name} at {transfer.from_location}. '
                    f'Available: {stock.quantity}, Requested: {line.qty}'
                )
        except Stock.DoesNotExist:
            raise InsufficientStockError(
                f'No stock found for {line.product.name} at {transfer.from_location}'
            )

    # Process lines
    for line in transfer.lines.select_related('product', 'unit'):
        # Transfer out
        StockMove.objects.create(
            product=line.product,
            from_location=transfer.from_location,
            to_location=None,
            quantity=line.qty,
            move_type='transfer_out',
            reference_type='Transfer',
            reference_id=transfer.pk,
            reference_ref=transfer.ref,
            created_by=user,
        )

        # Transfer in
        StockMove.objects.create(
            product=line.product,
            from_location=None,
            to_location=transfer.to_location,
            quantity=line.qty,
            move_type='transfer_in',
            reference_type='Transfer',
            reference_id=transfer.pk,
            reference_ref=transfer.ref,
            created_by=user,
        )

        # Decrement source
        stock_from = Stock.objects.get(
            product=line.product,
            location=transfer.from_location,
        )
        stock_from.quantity -= line.qty
        stock_from.save()

        # Increment destination
        stock_to, created = Stock.objects.get_or_create(
            product=line.product,
            location=transfer.to_location,
            defaults={'quantity': 0},
        )
        stock_to.quantity += line.qty
        stock_to.save()

    transfer.status = 'done'
    transfer.validated_by = user
    transfer.validated_at = timezone.now()
    transfer.save()

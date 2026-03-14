"""
Celery tasks for stock alerts.
"""

from celery import shared_task
from apps.ledger.models import Stock
from apps.alerts.models import Notification


@shared_task
def check_low_stock():
    """
    Query all Stock where quantity <= product.reorder_point.
    Create Notification if one doesn't already exist for this product+location.
    """
    stocks = Stock.objects.select_related('product', 'location').filter(
        product__is_active=True,
    )

    for stock in stocks:
        if stock.quantity <= 0:
            # Out of stock
            exists = Notification.objects.filter(
                product=stock.product,
                location=stock.location,
                type='out_of_stock',
                is_read=False,
            ).exists()
            if not exists:
                Notification.objects.create(
                    product=stock.product,
                    location=stock.location,
                    type='out_of_stock',
                    message=f'{stock.product.name} is OUT OF STOCK at {stock.location}.',
                )
        elif stock.quantity <= stock.product.reorder_point:
            # Low stock
            exists = Notification.objects.filter(
                product=stock.product,
                location=stock.location,
                type='low_stock',
                is_read=False,
            ).exists()
            if not exists:
                Notification.objects.create(
                    product=stock.product,
                    location=stock.location,
                    type='low_stock',
                    message=(
                        f'{stock.product.name} is LOW at {stock.location}. '
                        f'Current: {stock.quantity}, Reorder point: {stock.product.reorder_point}.'
                    ),
                )

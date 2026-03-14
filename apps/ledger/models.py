from django.conf import settings
from django.db import models


class StockMove(models.Model):
    """
    Core ledger — immutable stock movement records.
    Never delete or update records from here.
    """
    MOVE_TYPE_CHOICES = [
        ('receipt', 'Receipt'),
        ('delivery', 'Delivery'),
        ('transfer_out', 'Transfer Out'),
        ('transfer_in', 'Transfer In'),
        ('adjustment_in', 'Adjustment In'),
        ('adjustment_out', 'Adjustment Out'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_moves',
    )
    from_location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moves_out',
    )
    to_location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moves_in',
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text='Always positive',
    )
    move_type = models.CharField(max_length=20, choices=MOVE_TYPE_CHOICES)
    reference_type = models.CharField(
        max_length=50,
        help_text='e.g. Receipt, Delivery, Transfer, Adjustment',
    )
    reference_id = models.PositiveIntegerField(
        help_text='Links to source document PK',
    )
    reference_ref = models.CharField(
        max_length=20,
        help_text='e.g. RCP-2026-0042',
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_moves',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.move_type} | {self.product.name} | qty={self.quantity} | {self.reference_ref}'


class Stock(models.Model):
    """Current stock snapshot per product per location."""
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_records',
    )
    location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.PROTECT,
        related_name='stock_records',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product', 'location')
        ordering = ['product', 'location']

    def __str__(self):
        return f'{self.product.name} @ {self.location} = {self.quantity}'

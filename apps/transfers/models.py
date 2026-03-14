from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_transfer_ref():
    """Generate ref: TRF-YYYY-NNNN"""
    from apps.transfers.models import Transfer
    year = timezone.now().year
    count = Transfer.objects.filter(created_at__year=year).count() + 1
    return f'TRF-{year}-{count:04d}'


class Transfer(models.Model):
    """Internal stock transfer between locations."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    ref = models.CharField(max_length=20, unique=True, blank=True)
    from_location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.PROTECT,
        related_name='transfers_out',
    )
    to_location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.PROTECT,
        related_name='transfers_in',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_transfers',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_transfers',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ref} ({self.from_location} → {self.to_location})'

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref = generate_transfer_ref()
        super().save(*args, **kwargs)


class TransferLine(models.Model):
    """Line item on a transfer."""
    transfer = models.ForeignKey(
        Transfer,
        on_delete=models.CASCADE,
        related_name='lines',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='transfer_lines',
    )
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.ForeignKey(
        'products.UnitOfMeasure',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f'{self.transfer.ref} — {self.product.name} ({self.qty})'

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_delivery_ref():
    """Generate ref: DLV-YYYY-NNNN"""
    from apps.deliveries.models import Delivery
    year = timezone.now().year
    count = Delivery.objects.filter(created_at__year=year).count() + 1
    return f'DLV-{year}-{count:04d}'


class Delivery(models.Model):
    """Outgoing stock delivery."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    ref = models.CharField(max_length=20, unique=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_contact = models.CharField(max_length=255, blank=True)
    source = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.PROTECT,
        related_name='deliveries',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_deliveries',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_deliveries',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ref} — {self.customer_name}'

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref = generate_delivery_ref()
        super().save(*args, **kwargs)


class DeliveryLine(models.Model):
    """Line item on a delivery."""
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='lines',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='delivery_lines',
    )
    requested_qty = models.DecimalField(max_digits=12, decimal_places=2)
    delivered_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.ForeignKey(
        'products.UnitOfMeasure',
        on_delete=models.PROTECT,
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.delivery.ref} — {self.product.name} (req: {self.requested_qty})'

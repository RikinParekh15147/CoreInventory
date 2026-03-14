from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_receipt_ref():
    """Generate ref: RCP-YYYY-NNNN"""
    from apps.receipts.models import Receipt
    year = timezone.now().year
    count = Receipt.objects.filter(created_at__year=year).count() + 1
    return f'RCP-{year}-{count:04d}'


class Receipt(models.Model):
    """Incoming stock receipt."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    ref = models.CharField(max_length=20, unique=True, blank=True)
    supplier = models.ForeignKey(
        'contacts.Supplier',
        on_delete=models.PROTECT,
        related_name='receipts',
        null=True,
        blank=True,
    )
    supplier_name = models.CharField(max_length=255, help_text="Legacy name field")
    supplier_contact = models.CharField(max_length=255, blank=True)
    destination = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.PROTECT,
        related_name='receipts',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_receipts',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_receipts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ref} — {self.supplier_name}'

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref = generate_receipt_ref()
        super().save(*args, **kwargs)


class ReceiptLine(models.Model):
    """Line item on a receipt."""
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='lines',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='receipt_lines',
    )
    expected_qty = models.DecimalField(max_digits=12, decimal_places=2)
    received_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.ForeignKey(
        'products.UnitOfMeasure',
        on_delete=models.PROTECT,
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.receipt.ref} — {self.product.name} (exp: {self.expected_qty})'

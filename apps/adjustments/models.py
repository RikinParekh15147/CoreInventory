from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_adjustment_ref():
    """Generate ref: ADJ-YYYY-NNNN"""
    from apps.adjustments.models import Adjustment
    year = timezone.now().year
    count = Adjustment.objects.filter(created_at__year=year).count() + 1
    return f'ADJ-{year}-{count:04d}'


class Adjustment(models.Model):
    """Stock adjustment for corrections."""
    REASON_CHOICES = [
        ('damage', 'Damage'),
        ('theft', 'Theft'),
        ('count_correction', 'Count Correction'),
        ('expiry', 'Expiry'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    ref = models.CharField(max_length=20, unique=True, blank=True)
    location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.PROTECT,
        related_name='adjustments',
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_adjustments',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_adjustments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ref} — {self.get_reason_display()}'

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref = generate_adjustment_ref()
        super().save(*args, **kwargs)


class AdjustmentLine(models.Model):
    """Line item on an adjustment."""
    adjustment = models.ForeignKey(
        Adjustment,
        on_delete=models.CASCADE,
        related_name='lines',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='adjustment_lines',
    )
    recorded_qty = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text='What the system says',
    )
    actual_qty = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text='What was physically counted',
    )
    unit = models.ForeignKey(
        'products.UnitOfMeasure',
        on_delete=models.PROTECT,
    )

    @property
    def difference(self):
        """actual_qty - recorded_qty"""
        return self.actual_qty - self.recorded_qty

    def __str__(self):
        return f'{self.adjustment.ref} — {self.product.name} (diff: {self.difference})'

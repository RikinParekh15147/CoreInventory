import random
import string
from django.db import models
from django.db.models import Sum


class ProductCategory(models.Model):
    """Product category with optional parent for nesting."""
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Product Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class UnitOfMeasure(models.Model):
    """Unit of measure (e.g. kg, pcs, litre)."""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


def generate_sku():
    """Generate a unique SKU: PRD-XXXXXX."""
    chars = string.ascii_uppercase + string.digits
    return 'PRD-' + ''.join(random.choices(chars, k=6))


class Product(models.Model):
    """Product master record."""
    name = models.CharField(max_length=255)
    sku = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text='Auto-generated if blank: PRD-XXXXXX',
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='products',
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    reorder_point = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Low stock threshold',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.sku})'

    def save(self, *args, **kwargs):
        if not self.sku:
            # Generate unique SKU
            for _ in range(10):
                sku = generate_sku()
                if not Product.objects.filter(sku=sku).exists():
                    self.sku = sku
                    break
        super().save(*args, **kwargs)

    @property
    def total_stock(self):
        """Sum of all Stock.quantity for this product."""
        from apps.ledger.models import Stock
        result = Stock.objects.filter(
            product=self
        ).aggregate(total=Sum('quantity'))
        return result['total'] or 0

    @property
    def is_low_stock(self):
        """True if total_stock <= reorder_point."""
        return self.total_stock <= self.reorder_point

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Low-stock / out-of-stock / AI alert notification."""
    TYPE_CHOICES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('ai_insight', 'AI Insight'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        'warehouses.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.type == 'ai_insight':
            return f'AI Insight for {self.user}'
        return f'{self.get_type_display()}: {self.product.name if self.product else "N/A"}'

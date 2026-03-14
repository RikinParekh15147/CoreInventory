from django.db import models


class Warehouse(models.Model):
    """Physical warehouse."""
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    """Specific location within a warehouse (e.g. Rack A-3)."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='locations',
    )
    name = models.CharField(max_length=255, help_text='e.g. Rack A-3, Production Floor')
    coordinates = models.CharField(max_length=100, blank=True, help_text='Optional coordinates')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['warehouse', 'name']

    def __str__(self):
        return f'{self.warehouse.name} / {self.name}'

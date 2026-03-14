from django.contrib import admin
from .models import Warehouse, Location


class LocationInline(admin.TabularInline):
    model = Location
    extra = 1


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    inlines = [LocationInline]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'is_active')
    list_filter = ('warehouse', 'is_active')

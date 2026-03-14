from django.contrib import admin
from .models import Delivery, DeliveryLine


class DeliveryLineInline(admin.TabularInline):
    model = DeliveryLine
    extra = 1


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('ref', 'customer_name', 'source', 'status', 'scheduled_date', 'created_by')
    list_filter = ('status',)
    search_fields = ('ref', 'customer_name')
    inlines = [DeliveryLineInline]

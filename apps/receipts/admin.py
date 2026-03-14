from django.contrib import admin
from .models import Receipt, ReceiptLine


class ReceiptLineInline(admin.TabularInline):
    model = ReceiptLine
    extra = 1


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('ref', 'supplier_name', 'destination', 'status', 'scheduled_date', 'created_by')
    list_filter = ('status',)
    search_fields = ('ref', 'supplier_name')
    inlines = [ReceiptLineInline]

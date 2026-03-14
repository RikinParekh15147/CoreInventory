from django.contrib import admin
from .models import StockMove, Stock


@admin.register(StockMove)
class StockMoveAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'move_type', 'quantity', 'from_location', 'to_location', 'reference_ref', 'created_by')
    list_filter = ('move_type', 'created_at')
    search_fields = ('product__name', 'reference_ref')
    readonly_fields = ('product', 'from_location', 'to_location', 'quantity', 'move_type',
                       'reference_type', 'reference_id', 'reference_ref', 'notes', 'created_by', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'quantity')
    list_filter = ('location__warehouse',)
    search_fields = ('product__name',)

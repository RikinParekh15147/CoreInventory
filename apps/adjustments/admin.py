from django.contrib import admin
from .models import Adjustment, AdjustmentLine


class AdjustmentLineInline(admin.TabularInline):
    model = AdjustmentLine
    extra = 1


@admin.register(Adjustment)
class AdjustmentAdmin(admin.ModelAdmin):
    list_display = ('ref', 'location', 'reason', 'status', 'created_by')
    list_filter = ('status', 'reason')
    search_fields = ('ref',)
    inlines = [AdjustmentLineInline]

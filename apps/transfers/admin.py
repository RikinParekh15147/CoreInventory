from django.contrib import admin
from .models import Transfer, TransferLine


class TransferLineInline(admin.TabularInline):
    model = TransferLine
    extra = 1


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('ref', 'from_location', 'to_location', 'status', 'scheduled_date', 'created_by')
    list_filter = ('status',)
    search_fields = ('ref',)
    inlines = [TransferLineInline]

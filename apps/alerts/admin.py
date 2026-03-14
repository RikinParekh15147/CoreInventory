from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('product__name', 'message')

from django.contrib import admin
from .models import Supplier, Customer

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('is_active',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('is_active',)

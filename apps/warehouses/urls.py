from django.urls import path

from . import views

app_name = 'warehouses'

urlpatterns = [
    path('warehouses/', views.warehouse_list, name='list'),
    path('warehouses/<int:pk>/edit/', views.warehouse_edit, name='edit'),
]

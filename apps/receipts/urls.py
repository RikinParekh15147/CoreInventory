from django.urls import path
from . import views

app_name = 'receipts'

urlpatterns = [
    path('', views.receipt_list, name='list'),
    path('new/', views.receipt_create, name='create'),
    path('<int:pk>/', views.receipt_detail, name='detail'),
    path('<int:pk>/edit/', views.receipt_edit, name='edit'),
    path('<int:pk>/status/', views.receipt_change_status, name='change-status'),
]

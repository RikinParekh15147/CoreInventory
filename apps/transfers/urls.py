from django.urls import path
from . import views

app_name = 'transfers'

urlpatterns = [
    path('', views.transfer_list, name='list'),
    path('new/', views.transfer_create, name='create'),
    path('<int:pk>/', views.transfer_detail, name='detail'),
    path('<int:pk>/edit/', views.transfer_edit, name='edit'),
    path('<int:pk>/status/', views.transfer_change_status, name='change-status'),
]

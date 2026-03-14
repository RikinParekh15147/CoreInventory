from django.urls import path
from . import views

app_name = 'access'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_list, name='user-list'),
    path('users/<int:pk>/edit/', views.user_edit, name='user-edit'),
    path('roles/', views.role_list, name='role-list'),
    path('roles/<int:pk>/edit/', views.role_edit, name='role-edit'),
    path('warehouses/', views.warehouse_list, name='warehouse-list'),
    path('warehouses/<int:pk>/edit/', views.warehouse_edit, name='warehouse-edit'),
]

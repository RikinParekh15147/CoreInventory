from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path('', views.delivery_list, name='list'),
    path('new/', views.delivery_create, name='create'),
    path('<int:pk>/', views.delivery_detail, name='detail'),
    path('<int:pk>/edit/', views.delivery_edit, name='edit'),
    path('<int:pk>/status/', views.delivery_change_status, name='change-status'),
]

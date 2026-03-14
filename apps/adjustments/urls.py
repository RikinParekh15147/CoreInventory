from django.urls import path
from . import views

app_name = 'adjustments'

urlpatterns = [
    path('', views.adjustment_list, name='list'),
    path('new/', views.adjustment_create, name='create'),
    path('<int:pk>/', views.adjustment_detail, name='detail'),
    path('<int:pk>/edit/', views.adjustment_edit, name='edit'),
    path('<int:pk>/validate/', views.adjustment_validate, name='validate'),
]

from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('count/', views.notification_count, name='count'),
]

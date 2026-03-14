"""
AI Chat URL configuration.
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('send/', views.chat_send, name='send'),
    path('execute/', views.chat_execute, name='execute'),
]

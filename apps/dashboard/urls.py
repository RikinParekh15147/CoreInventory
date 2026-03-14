from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('kpis/', views.kpis_partial, name='kpis'),
    path('generate-ai-insights/', views.generate_ai_insights, name='generate_ai_insights'),
]

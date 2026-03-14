from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('pending-approval/', views.pending_approval_view, name='pending_approval'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/verify/', views.password_reset_verify_view, name='password_reset_verify'),
]

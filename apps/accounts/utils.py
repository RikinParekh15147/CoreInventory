import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def generate_otp(length=6):
    """Generate a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(user, otp, context='password_reset'):
    """Send an OTP email to the user."""
    send_otp_to_email(user.email, otp, user.full_name, context=context)
    
    # Update user's OTP fields
    user.otp_code = otp
    user.otp_expiry = timezone.now() + timedelta(minutes=10)
    user.save()

def send_otp_to_email(email, otp, full_name=None, context='signup'):
    """Send an OTP email to a specific email address (user might not exist yet)."""
    print(f"DEBUG: Preparing to send OTP for {email}")
    print(f"DEBUG: EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    
    name = full_name or "User"
    if context == 'password_reset':
        subject = 'Password Reset — CoreInventory'
        message = f'Hi {name},\n\nWe received a request to reset your password. Your password reset verification code is: {otp}\n\nThis code will expire in 10 minutes.\n\nIf you did not request this, please ignore this email.'
    else:
        subject = 'Your CoreInventory Verification Code'
        message = f'Hi {name},\n\nYour verification code is: {otp}\n\nThis code will expire in 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"DEBUG: send_mail call finished for {email}")
    except Exception as e:
        print(f"DEBUG: send_mail failed. Error: {str(e)}")
        raise e

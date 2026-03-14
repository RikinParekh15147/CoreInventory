import os
import django
from django.conf import settings
from django.core.mail import send_mail

# Mocking settings if not running in django context, but better to use django context
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

def test_send():
    print(f"Attempting to send test email from: {settings.EMAIL_HOST_USER}")
    try:
        subject = 'Manual OTP Verification — CoreInventory'
        message = 'Your manual verification code is: 998877\n\nThis is a test to verify SMTP delivery to your inbox.'
        recipient_list = ['rikinparekh15147@gmail.com']
        
        send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            recipient_list,
            fail_silently=False
        )
        print("Success: Email sent successfully!")
    except Exception as e:
        print(f"Error: Failed to send email. Reasons: {str(e)}")

if __name__ == "__main__":
    test_send()

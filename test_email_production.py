import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.accounts.utils import send_otp_to_email

def test_actual_function():
    email = 'rikinparekh15147@gmail.com'
    otp = '123456'
    full_name = 'Rikin'
    print(f"Testing send_otp_to_email function for: {email}")
    try:
        send_otp_to_email(email, otp, full_name)
        print("Success: Function send_otp_to_email executed successfully!")
    except Exception as e:
        print(f"Error: Function failed. Reason: {str(e)}")

if __name__ == "__main__":
    test_actual_function()

"""
Account views — profile management.
"""

from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .forms import EnhancedSignupForm, OTPVerificationForm
from .utils import generate_otp, send_otp_email, send_otp_to_email
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import timedelta

User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        form = EnhancedSignupForm(request.POST)
        if form.is_valid():
            # Store signup data in session instead of saving user
            signup_data = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'role_id': form.cleaned_data['role'].id,
                'password': make_password(form.cleaned_data['password']),
            }
            
            # Generate and send OTP
            otp = generate_otp()
            send_otp_to_email(signup_data['email'], otp, signup_data['full_name'])
            
            # Store in session
            request.session['signup_data'] = signup_data
            request.session['signup_otp'] = {
                'code': otp,
                'expiry': (timezone.now() + timedelta(minutes=10)).isoformat()
            }
            print(f"DEBUG: Signup data stored in session. OTP: {otp}")
            
            messages.info(request, "A verification code has been sent to your email.")
            return redirect('accounts:verify_otp')
    else:
        form = EnhancedSignupForm()
    return render(request, 'account/signup.html', {'form': form})

def verify_otp_view(request):
    signup_data = request.session.get('signup_data')
    signup_otp = request.session.get('signup_otp')
    print(f"DEBUG: verify_otp_view accessed. signup_data: {signup_data is not None}, signup_otp: {signup_otp is not None}")
    
    if not signup_data or not signup_otp:
        return redirect('accounts:signup')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            expiry = timezone.datetime.fromisoformat(signup_otp['expiry'])
            
            if signup_otp['code'] == otp_code and expiry > timezone.now():
                # OTP is valid, create the user now
                user = User.objects.create(
                    email=signup_data['email'],
                    full_name=signup_data['full_name'],
                    role_id=signup_data['role_id'],
                    password=signup_data['password'],
                    is_active=True,
                    is_approved=False
                )
                
                # Clear session
                del request.session['signup_data']
                del request.session['signup_otp']
                
                messages.success(request, "Email verified successfully! Your account is now awaiting admin approval.")
                return redirect('accounts:pending_approval')
            else:
                messages.error(request, "Invalid or expired verification code.")
    else:
        form = OTPVerificationForm()
    
    return render(request, 'account/verify_otp.html', {'form': form, 'email': signup_data['email']})

def pending_approval_view(request):
    return render(request, 'account/pending_approval.html')

def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            send_otp_email(user, otp)
            request.session['reset_user_id'] = user.id
            messages.info(request, "A password reset code has been sent to your email.")
            return redirect('accounts:password_reset_verify')
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
    return render(request, 'account/password_reset_request.html')

def password_reset_verify_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('accounts:password_reset_request')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('accounts:password_reset_request')

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if user.otp_code == otp_code and user.otp_expiry > timezone.now():
            if new_password == confirm_password:
                user.set_password(new_password)
                user.otp_code = None
                user.otp_expiry = None
                user.save()
                del request.session['reset_user_id']
                messages.success(request, "Password has been reset successfully. You can now log in.")
                return redirect('account_login')
            else:
                messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "Invalid or expired verification code.")
            
    return render(request, 'account/password_reset_verify.html', {'email': user.email})

@login_required
def profile_view(request):
    """User profile view — display and edit basic info."""
    user = request.user

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        user.full_name = full_name
        user.phone = phone
        user.save(update_fields=['full_name', 'phone'])

        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')

    return render(request, 'account/profile.html', {'profile_user': user})


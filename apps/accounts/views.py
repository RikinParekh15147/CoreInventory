"""
Account views — profile management.
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


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

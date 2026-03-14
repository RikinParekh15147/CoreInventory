from django import forms
from django.contrib.auth import get_user_model
from apps.access.models import Role

User = get_user_model()

class EnhancedSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a password',
        'class': 'w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
        'class': 'w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition'
    }))
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        empty_label="Select your role",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'class': 'w-full px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-white text-center text-2xl tracking-widest focus:border-primary focus:ring-1 focus:ring-primary outline-none transition'
        })
    )

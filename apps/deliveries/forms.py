"""
Delivery forms.
"""
from django import forms
from .models import Delivery, DeliveryLine

INPUT_CLASS = 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['customer_name', 'customer_contact', 'source', 'scheduled_date', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Customer name'}),
            'customer_contact': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Contact info'}),
            'source': forms.Select(attrs={'class': INPUT_CLASS}),
            'scheduled_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3}),
        }


class DeliveryLineForm(forms.ModelForm):
    class Meta:
        model = DeliveryLine
        fields = ['product', 'requested_qty', 'delivered_qty', 'unit', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': INPUT_CLASS}),
            'requested_qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0'}),
            'delivered_qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0'}),
            'unit': forms.Select(attrs={'class': INPUT_CLASS}),
            'notes': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }


DeliveryLineFormSet = forms.inlineformset_factory(
    Delivery, DeliveryLine, form=DeliveryLineForm, extra=1, can_delete=True,
)

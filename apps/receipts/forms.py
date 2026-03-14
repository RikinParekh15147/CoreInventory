"""
Receipt forms.
"""

from django import forms
from .models import Receipt, ReceiptLine
from apps.products.models import Product, UnitOfMeasure
from apps.warehouses.models import Location

INPUT_CLASS = 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['supplier', 'supplier_name', 'supplier_contact', 'destination', 'scheduled_date', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': INPUT_CLASS}),
            'supplier_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Legacy Supplier Name (optional)'}),
            'supplier_contact': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Contact info'}),
            'destination': forms.Select(attrs={'class': INPUT_CLASS}),
            'scheduled_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3}),
        }


class ReceiptLineForm(forms.ModelForm):
    class Meta:
        model = ReceiptLine
        fields = ['product', 'expected_qty', 'received_qty', 'unit', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': INPUT_CLASS}),
            'expected_qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0'}),
            'received_qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0'}),
            'unit': forms.Select(attrs={'class': INPUT_CLASS}),
            'notes': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Line notes'}),
        }


ReceiptLineFormSet = forms.inlineformset_factory(
    Receipt, ReceiptLine,
    form=ReceiptLineForm,
    extra=1, can_delete=True,
)

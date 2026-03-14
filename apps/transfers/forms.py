"""
Transfer forms.
"""
from django import forms
from .models import Transfer, TransferLine

INPUT_CLASS = 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['from_location', 'to_location', 'scheduled_date', 'notes']
        widgets = {
            'from_location': forms.Select(attrs={'class': INPUT_CLASS}),
            'to_location': forms.Select(attrs={'class': INPUT_CLASS}),
            'scheduled_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3}),
        }


class TransferLineForm(forms.ModelForm):
    class Meta:
        model = TransferLine
        fields = ['product', 'qty', 'unit']
        widgets = {
            'product': forms.Select(attrs={'class': INPUT_CLASS}),
            'qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0'}),
            'unit': forms.Select(attrs={'class': INPUT_CLASS}),
        }


TransferLineFormSet = forms.inlineformset_factory(
    Transfer, TransferLine, form=TransferLineForm, extra=1, can_delete=True,
)

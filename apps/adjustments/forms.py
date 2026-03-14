"""
Adjustment forms.
"""
from django import forms
from .models import Adjustment, AdjustmentLine

INPUT_CLASS = 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'


class AdjustmentForm(forms.ModelForm):
    class Meta:
        model = Adjustment
        fields = ['location', 'reason', 'notes']
        widgets = {
            'location': forms.Select(attrs={'class': INPUT_CLASS}),
            'reason': forms.Select(attrs={'class': INPUT_CLASS}),
            'notes': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3}),
        }


class AdjustmentLineForm(forms.ModelForm):
    class Meta:
        model = AdjustmentLine
        fields = ['product', 'recorded_qty', 'actual_qty', 'unit']
        widgets = {
            'product': forms.Select(attrs={'class': INPUT_CLASS}),
            'recorded_qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'}),
            'actual_qty': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': INPUT_CLASS}),
        }


AdjustmentLineFormSet = forms.inlineformset_factory(
    Adjustment, AdjustmentLine, form=AdjustmentLineForm, extra=1, can_delete=True,
)

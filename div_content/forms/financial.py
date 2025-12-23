# -------------------------------------------------------------------
#                    FORMS – FINANCIAL
# -------------------------------------------------------------------

from django import forms
from div_content.models import Financialtransaction


class FinancialTransactionForm(forms.ModelForm):

    class Meta:
        model = Financialtransaction
        fields = [
            'amount',
            'currency',
            'direction',
            'sourcetype',
            'sourceid',
            'sourceref',
            'platform',
            'note',
        ]

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'style': 'max-width:80px'}),
            'direction': forms.Select(attrs={'class': 'form-control'}),
            'sourcetype': forms.Select(attrs={'class': 'form-control'}),
            'sourceid': forms.NumberInput(attrs={'class': 'form-control'}),
            'sourceref': forms.TextInput(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

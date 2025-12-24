# -------------------------------------------------------------------
#                    FORMS – FINANCIAL
# -------------------------------------------------------------------

from django import forms
from div_content.models import Financialtransaction

class FinancialTransactionForm(forms.ModelForm):

    class Meta:
        model = Financialtransaction
        fields = [
            'eventdate',
            'amount',
            'currency',
            'direction',
            'sourcetype',
            'sourceid',
            'sourceref',
            'platform',
            'note',
        ]

        BASE_INPUT = 'w-full rounded-lg border border-gray-300 bg-white px-3 py-2 focus:border-green-500 focus:ring focus:ring-green-200'

        widgets = {
            'eventdate': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': BASE_INPUT,
            }),
            'amount': forms.NumberInput(attrs={
                'class': BASE_INPUT,
            }),
            'currency': forms.TextInput(attrs={
                'class': BASE_INPUT + ' max-w-[90px]',
            }),
            'direction': forms.Select(attrs={
                'class': BASE_INPUT,
            }),
            'sourcetype': forms.Select(attrs={
                'class': BASE_INPUT,
            }),
            'sourceid': forms.NumberInput(attrs={
                'class': BASE_INPUT,
            }),
            'sourceref': forms.TextInput(attrs={
                'class': BASE_INPUT,
            }),
            'platform': forms.Select(attrs={
                'class': BASE_INPUT,
            }),
            'note': forms.Textarea(attrs={
                'class': BASE_INPUT,
                'rows': 3,
                'placeholder': '(volitelná poznámka)',
            }),
        }
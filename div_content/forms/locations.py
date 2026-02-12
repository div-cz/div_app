# -------------------------------------------------------------------
#                    FORMS.LOCATION.PY
# -------------------------------------------------------------------

from django import forms
from div_content.models import Metalocation, Metatype, Metauniversum


class LocationForm(forms.ModelForm):
    class Meta:
        model = Metalocation
        fields = [
            'locationname',
            'locationnamecz',
            'locationtypeid',
            'parentlocation',
            'universum',
            'locationdescription',
            'locationadress',
            'gpsx',
            'gpsy',
            'divrating',
        ]

        widgets = {
            'locationname': forms.TextInput(attrs={'class': 'form-control'}),
            'locationnamecz': forms.TextInput(attrs={'class': 'form-control'}),
            'locationdescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'locationadress': forms.TextInput(attrs={'class': 'form-control'}),
            'gpsx': forms.TextInput(attrs={'class': 'form-control'}),
            'gpsy': forms.TextInput(attrs={'class': 'form-control'}),
            'divrating': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    parentlocation = forms.ModelChoiceField(
        queryset=Metalocation.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    universum = forms.ModelChoiceField(
        queryset=Metauniversum.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    locationtypeid = forms.ModelChoiceField(
        queryset=Metatype.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


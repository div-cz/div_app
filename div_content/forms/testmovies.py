from django import forms

class MyForm(forms.Form):
    arg1 = forms.CharField(label="ID Filmu - OD", max_length=100)
    arg2 = forms.CharField(label="ID Filmu - DO", max_length=100,required=False)
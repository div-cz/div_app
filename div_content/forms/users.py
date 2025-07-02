# FORMS.USERS.PY

from django import forms
from django.contrib.auth.models import User
from div_content.models import Userprofile, Usermessage
from datetime import date #new


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['bio', 'avatar', 'birthdate', 'location', 'bankaccount']

    def clean_birthdate(self):#new
        birthdate = self.cleaned_data.get('birthdate')
        if birthdate and birthdate > date.today():
            raise forms.ValidationError("Datum narození nemůže být v budoucnosti.")
        return birthdate


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Jméno")
    email = forms.EmailField(label="E-mail")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), label="Zpráva")


class UserMessageForm(forms.ModelForm):
    class Meta:
        model = Usermessage
        fields = ["message"]
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control rich-editor',
                'placeholder': 'Napiš zprávu...',
                'rows': 3
            }),
        }
    
    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        if not message:
            raise forms.ValidationError("Posíláš prázdnou zprávu!")
        return message


class UserBankAccountForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['bankaccount']
        widgets = {
            'bankaccount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '119-5555555/0500'}),
        }




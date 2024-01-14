# FORMS.USERS.PY

from django import forms
from django.contrib.auth.models import User
from div_content.models import Userprofile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['bio', 'profilepicture', 'birthdate', 'location']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Jméno")
    email = forms.EmailField(label="E-mail")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), label="Zpráva")
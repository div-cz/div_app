from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from div_content.models import Moviecomments
"""
class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Nove uzivatelske jmeno', max_length=255, required=True)
    email = forms.EmailField(label='E-mail', max_length=255, required=True)
    password1 = forms.CharField(label='Nove heslo', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Potvrzeni hesla', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('username', css_class='form-control', wrapper_class='mb-3'),
            Field('email', css_class='form-control', wrapper_class='mb-3'),
            Field('password1', css_class='form-control', wrapper_class='mb-3'),
            Field('password2', css_class='form-control', wrapper_class='mb-3'),
            ButtonHolder(
                Submit('submit', 'Registrovat', css_class='btn btn-success')
            )
        )"""

# use in movies/movie_detail.html
class Commentform(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'bg-dark text-white w-100',  'style': 'height:120px'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = Moviecomments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


# FORMS.BOOKS.PY
# forms.books.py
from django import forms
from django.contrib.auth.models import User
from div_content.models import Bookcomments, Bookcharacter, Bookquotes, Userprofile

class BookAddForm(forms.Form):
    identifier = forms.CharField(label='ISBN nebo Google ID', max_length=255)



class SearchFormBooks(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)




class CommentFormBook(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-100',  'style': 'height:120px'})) #bg-dark text-white 

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = Bookcomments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class Bookquoteform(forms.ModelForm):
    characterid = forms.ModelChoiceField(
        queryset=Bookcharacter.objects.all(),
        required=False,
        label="Postava"
    )
    page_number = forms.IntegerField(
        required=False,
        label="Strana"
    )
    
    class Meta:
        model = Bookquotes
        fields = ['quote', 'characterid', 'page_number']
        labels = {
            'quote': 'Citát',
            'characterid': 'Postava',
            'page_number': 'Strana',
        }
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
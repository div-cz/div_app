# FORMS.BOOKS.PY
# forms.books.py
from django import forms

class BookAddForm(forms.Form):
    identifier = forms.CharField(label='ISBN nebo Google ID', max_length=255)








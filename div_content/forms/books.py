# FORMS.BOOKS.PY TEST
# forms.books.py
from django import forms
from django.contrib.auth.models import User
from div_content.models import Book, Bookcomments, Bookcharacter, Bookquotes, Userprofile

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


class BookCharacterForm(forms.ModelForm):
    class Meta:
        model = Bookcharacter
        fields = ['characterid', 'charactermain']
        widgets = {
            'characterid': forms.HiddenInput(),
            'charactermain': forms.Select(choices=[
                ('1', 'Hlavní postava'),
                ('0', 'Vedlejší postava'),
                ('3', 'Hlavní v části knihy'),
            ], attrs={'class': 'form-control'}),
        }
        labels = {
            'characterid': 'Postava',
            'charactermain': 'Typ postavy',
        }


class BookDivRatingForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['divrating']
        widgets = {
            'divrating': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }
        labels = {
            'divrating': 'DIV Rating (0-99)',
        }


class Bookquoteform(forms.ModelForm):
    bookcharacter = forms.ModelChoiceField(
        queryset=Bookcharacter.objects.all(),
        required=False,
        label="Postava"
    )
    chapter = forms.IntegerField(
        required=False,
        label="Kapitola"
    )
    
    class Meta:
        model = Bookquotes
        fields = ['quote', 'bookcharacter', 'chapter']  # Změna názvu pole zde
        labels = {
            'quote': '',
            'bookcharacter': 'Postava',  # Změna názvu pole zde
            'chapter': 'Kapitola',
        }
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        bookid = kwargs.pop('bookid', None)  # Získáme `bookid` z kwargs
        super().__init__(*args, **kwargs)
        if bookid:
            self.fields['bookcharacter'].queryset = Bookcharacter.objects.filter(bookid=bookid)

    def save(self, commit=True, book=None):
        instance = super(Bookquoteform, self).save(commit=False)
        # Nastavení správné instance Charactermeta na základě výběru z Bookcharacter
        bookcharacter = self.cleaned_data.get('bookcharacter', None)
        if bookcharacter:
            instance.characterid = bookcharacter.characterid
        else:
            instance.characterid = None  # Nastavení prázdného řetězce, pokud není vybrána postava

        # Nastavení bookid a následně authorid
        if book:
            instance.bookid = book
            instance.authorid = book.authorid

        if commit:
            instance.save()
        return instance
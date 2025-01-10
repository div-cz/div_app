# FORMS.BOOKS.PY TEST
# forms.books.py
from django import forms
from django.contrib.auth.models import User
from div_content.models import Book, Bookcomments, Bookcharacter, Booklisting, Bookquotes, Userprofile

class BookAddForm(forms.Form):
    identifier = forms.CharField(label='ISBN nebo Google ID', max_length=255)



class SearchFormBooks(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)


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


class BookListingForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=10, 
        required=True, 
        initial=100,
        label='Cena',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    shipping = forms.DecimalField(
        max_digits=10, 
        required=False, 
        initial=70,
        label='Poštovné',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    commission = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        initial=10, 
        label='Provize na chod webu',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    personal_pickup = forms.BooleanField(
        required=False, 
        label='Osobní převzetí',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = Booklisting
        fields = ['listingtype', 'price', 'shipping', 'commission', 'description', 'condition', 'location', 'personal_pickup']
        labels = {
            'listingtype': 'Typ',
            'price': 'Cena',
            'description': 'Popis',
            'condition': 'Stav',
            'location': 'Místo'
        }
        widgets = {
            'listingtype': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping': forms.NumberInput(attrs={'class': 'form-control'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'style': 'height:100px !important'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('listingtype'):
            self.initial['listingtype'] = 'SELL'
        if self.initial.get('listingtype') == 'GIVE':
            self.fields['price'].widget = forms.HiddenInput()
            self.fields['shipping'].widget = forms.HiddenInput()
            self.fields['commission'].widget = forms.HiddenInput()



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
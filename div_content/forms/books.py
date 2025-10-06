# -------------------------------------------------------------------
#                    FORMS.BOOKS.PY
# -------------------------------------------------------------------

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from div_content.models import Book, Bookauthor, Bookcomments, Bookcharacter, Booklisting, Bookpublisher, Bookquotes, Metagenre, Userprofile

#    FORMULÁŘE
# ManualBookForms
# Bookquoteform
# BookListingForm
# BookDivRatingForm
# BookCharacterForm
# CommentFormBook
# BookDivRatingForm
# SearchFormBooks
# BookAddForm
class ManualBookForm(forms.ModelForm):
    authorid = forms.ModelChoiceField(
        queryset=Bookauthor.objects.all().order_by('lastname', 'firstname'),
        required=False,
        label="Autor",
        empty_label="-- Vyberte autora --",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    genres = forms.ModelMultipleChoiceField(
        queryset=Metagenre.objects.all().order_by('genrenamecz'),
        required=False,
        label="Žánry",
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    
    publisher = forms.ModelChoiceField(
        queryset=Bookpublisher.objects.all().order_by('publishername'),
        required=False,
        label="Nakladatelství",
        empty_label="-- Vyberte nakladatelství --",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    cover_image = forms.ImageField(
        required=False,
        label="Obrázek obálky",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Book
        fields = [
            "title", "titlecz", "subtitle", "author", "authorid", 
            "year", "pages", "description", "language"
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Název knihy *'
            }),
            'titlecz': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Český název'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Podtitul'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jméno autora (text)'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1000,
                'max': 2030
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Popis knihy...'
            }),
            'language': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'title': 'Název knihy *',
            'titlecz': 'Český název',
            'subtitle': 'Podtitul',
            'author': 'Autor (text)',
            'year': 'Rok vydání',
            'pages': 'Počet stránek',
            'description': 'Popis',
            'language': 'Jazyk'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError("Název knihy je povinný.")
        return title

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1000 or year > 2030):
            raise ValidationError("Neplatný rok vydání.")
        return year

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
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
    #POSTAVA
    #bookcharacter = forms.ModelChoiceField(
    #    queryset=Bookcharacter.objects.all(),
    #    required=False,
    #    label="Postava"
    #)
    chapter = forms.IntegerField(
        required=False,
        label="Kapitola",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',  # CSS třída pro stylování
            'placeholder': '1'  # Pomůže s uživatelskou přívětivostí
        })
    )
    
    class Meta:
        model = Bookquotes
        fields = ['quote', 'chapter']  # Změna názvu pole zde
        labels = {
            'quote': '',
            #'bookcharacter': 'Postava',  
            'chapter': 'Kapitola',
        }
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        bookid = kwargs.pop('bookid', None)  # Získáme `bookid` z kwargs
        super().__init__(*args, **kwargs)
        # Postava
        #if bookid:
        #    self.fields['bookcharacter'].queryset = Bookcharacter.objects.filter(bookid=bookid)

    def save(self, commit=True, book=None):
        instance = super(Bookquoteform, self).save(commit=False)
        # Postava
        #bookcharacter = self.cleaned_data.get('bookcharacter', None)
        #if bookcharacter:
        #    instance.characterid = bookcharacter.characterid
        #else:
        #    instance.characterid = None  # Nastavení prázdného řetězce, pokud není vybrána postava

        # Nastavení bookid a následně authorid
        if book:
            instance.bookid = book
            instance.authorid = book.authorid

        if commit:
            instance.save()
        return instance
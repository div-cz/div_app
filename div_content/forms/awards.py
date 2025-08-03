# -------------------------------------------------------------------
#                    FORMS.AWARDS.PY
# -------------------------------------------------------------------

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.text import slugify


from div_content.models import Metaaward, Movieaward, Bookaward, Gameaward, Movie, Book, Game

class MetaawardForm(forms.ModelForm):
    """Formulář pro přidání/editaci hlavního ocenění"""
    
    class Meta:
        model = Metaaward
        fields = ['awardname', 'description', 'awardtype', 'year']
        widgets = {
            'awardname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Např. Akademie filmových umění a věd',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Popis ocenění...'
            }),
            'awardtype': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': 2030,
                'placeholder': '2024',
                'required': True
            })
        }
        labels = {
            'awardname': 'Název ocenění',
            'description': 'Popis',
            'awardtype': 'Typ ocenění',
            'year': 'Rok'
        }
        help_texts = {
            'awardname': 'Celý název ocenění (např. "Oscar", "Zlatý glóbus")',
            'description': 'Volitelný popis ocenění',
            'awardtype': 'Vyberte typ média, které toto ocenění hodnotí',
            'year': 'Rok, ve kterém se ocenění uděluje'
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1900 or year > 2030):
            raise ValidationError('Rok musí být mezi 1900 a 2030.')
        return year

    def clean(self):
        cleaned_data = super().clean()
        awardname = cleaned_data.get('awardname')
        year = cleaned_data.get('year')
        
        if awardname and year:
            self.instance.slug = slugify(awardname)
            # Kontrola, zda už neexistuje ocenění se stejným názvem a rokem
            existing = Metaaward.objects.filter(awardname=awardname, year=year)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(f'Ocenění "{awardname}" pro rok {year} již existuje.')
        
        return cleaned_data

class BaseNomineeForm(forms.ModelForm):
    """Základní formulář pro nominace"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Přidáme CSS třídy pro všechna pole
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class MovieawardForm(BaseNomineeForm):
    """Formulář pro filmové nominace"""
    
    # Custom field pro vyhledávání filmu
    movie_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Začněte psát název filmu...',
            'autocomplete': 'off'
        }),
        label='Vyhledat film',
        help_text='Začněte psát název filmu pro vyhledání'
    )
    
    class Meta:
        model = Movieaward
        fields = ['movieid', 'winner']
        widgets = {
            'movieid': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'winner': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'movieid': 'Film',
            'winner': 'Je vítěz?'
        }
        help_texts = {
            'movieid': 'Vyberte film z databáze',
            'winner': 'Zaškrtněte, pokud je tento film vítězem kategorie'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Omezíme výběr filmů na rozumný počet
        self.fields['movieid'].queryset = Movie.objects.all().order_by('title')[:100]
        
        # Pokud editujeme existující nominaci, předvyplníme vyhledávací pole
        if self.instance and self.instance.pk and self.instance.movieid:
            movie = self.instance.movieid
            self.fields['movie_search'].initial = f"{movie.titlecz or movie.title} ({movie.releaseyear})"
            
        if 'movieid' in self.data:
            try:
                movie_id = int(self.data.get('movieid'))
                self.fields['movieid'].queryset = Movie.objects.filter(movieid=movie_id)
            except (ValueError, TypeError):
                pass  # neplatné ID = ponecháme prázdný queryset


class BookawardForm(BaseNomineeForm):
    """Formulář pro knižní nominace"""
    
    book_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Začněte psát název knihy...',
            'autocomplete': 'off'
        }),
        label='Vyhledat knihu',
        help_text='Začněte psát název knihy pro vyhledání'
    )
    
    class Meta:
        model = Bookaward
        fields = ['bookid', 'winner']
        widgets = {
            'bookid': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'winner': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'bookid': 'Kniha',
            'winner': 'Je vítěz?'
        }
        help_texts = {
            'bookid': 'Vyberte knihu z databáze',
            'winner': 'Zaškrtněte, pokud je tato kniha vítězem kategorie'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bookid'].queryset = Book.objects.all().order_by('title')[:100]
        
        if self.instance and self.instance.pk and self.instance.bookid:
            book = self.instance.bookid
            self.fields['book_search'].initial = f"{book.titlecz or book.title} ({book.year}) - {book.author}"

        if 'bookid' in self.data:
            try:
                val = int(self.data.get('bookid'))
                self.fields['bookid'].queryset = book.objects.filter(pk=val)
            except (ValueError, TypeError):
                pass


class GameawardForm(BaseNomineeForm):
    """Formulář pro herní nominace"""
    
    game_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Začněte psát název hry...',
            'autocomplete': 'off'
        }),
        label='Vyhledat hru',
        help_text='Začněte psát název hry pro vyhledání'
    )
    
    class Meta:
        model = Gameaward
        fields = ['gameid', 'winner']
        widgets = {
            'gameid': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'winner': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'gameid': 'Hra',
            'winner': 'Je vítěz?'
        }
        help_texts = {
            'gameid': 'Vyberte hru z databáze',
            'winner': 'Zaškrtněte, pokud je tato hra vítězem kategorie'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gameid'].queryset = Game.objects.all().order_by('title')[:100]
        
        if self.instance and self.instance.pk and self.instance.gameid:
            game = self.instance.gameid
            self.fields['game_search'].initial = f"{game.titlecz or game.title} ({game.year})"
            
        if 'gameid' in self.data:
            try:
                val = int(self.data.get('gameid'))
                self.fields['gameid'].queryset = game.objects.filter(pk=val)
            except (ValueError, TypeError):
                pass


class AwardFilterForm(forms.Form):
    """Formulář pro filtrování ocenění"""
    
    AWARD_TYPE_CHOICES = [
        ('', 'Všechny typy'),
        ('film', 'Filmová'),
        ('book', 'Knižní'),
        ('game', 'Herní'),
    ]
    
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rok',
            'min': 1900,
            'max': 2030
        }),
        label='Rok'
    )
    
    awardtype = forms.ChoiceField(
        choices=AWARD_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Typ ocenění'
    )
    
    award_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Název ocenění'
        }),
        label='Název ocenění'
    )
    
    winners_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Pouze vítězové'
    )

class BulkNomineeForm(forms.Form):
    """Formulář pro hromadné přidání nominací"""
    
    nominees_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Zadejte názvy po řádcích...\nNapr.:\nTitanic\nForrest Gump\nPulp Fiction'
        }),
        label='Seznam nominovaných',
        help_text='Zadejte každý název na nový řádek'
    )
    
    all_winners = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Všichni jsou vítězové',
        help_text='Zaškrtněte, pokud jsou všichni zadaní nominanti vítězové'
    )
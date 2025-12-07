# forms.creators.py

from django import forms
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from div_content.models import Favorite, Characterbiography


#from django.contrib.auth.models import User

class CharacterBiographyForm(forms.ModelForm):
    class Meta:
        model = Characterbiography
        fields = [
            'biographyid',
            'characterborn',
            'characterdeath',
            'biographytextcz',
            'biographytext',
            'source',
            'externallink',
            'img',
            'notes',
        ]
        labels = {
            'characterborn': 'Datum narození',
            'characterdeath': 'Datum úmrtí',
            'biographytextcz': "Životopis (CZ)",
            'biographytext': "Životopis (EN)",
            'source': "Zdroj",
            'externallink': "URL adresa zdroje",
            'img': "URL obrázku",
            'notes': "Poznámky (interní)",
        }
        widgets = {
            'biographyid': forms.HiddenInput(),
            'biographytextcz': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'biographytext': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'externallink': forms.URLInput(attrs={'class': 'form-control'}),
            'img': forms.URLInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'characterborn': forms.TextInput(attrs={'class': 'form-control'}),
            'characterdeath': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }



class SearchFormCharacter(forms.Form):
    q = forms.CharField(label='Hledat postavu', max_length=255)


class FavoriteFormCharacter(forms.Form):
    object_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self):
        content_type_id = 13  # Napevno pro Characters
        object_id = self.cleaned_data['object_id']

        # Zajištění, že existuje uživatel
        if not self.user:
            raise ValueError("Uživatel není přihlášen.")

        # Najdeme nebo vytvoříme záznam o oblíbenosti
        favorite, created = Favorite.objects.get_or_create(
            user=self.user,
            content_type_id=content_type_id,
            object_id=object_id,
        )

        if not created:
            favorite.delete()  # Pokud záznam existuje, smaže se (toggle)
            return False  # Označuje, že byl odebrán

        return True  # Označuje, že byl přidán
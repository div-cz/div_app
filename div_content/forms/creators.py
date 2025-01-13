# forms.creators.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from div_content.models import Creator, Creatorbiography, Favorite


class CreatorBiographyForm(forms.ModelForm):
    class Meta:
        model = Creatorbiography
        fields = [
            'biographyid', 'biographytextcz', 'source', 
            'externallink', 'imageurl'
        ]
        labels = {
            'biographytextcz': "Životopis",
            'source': "Zdroj",
            'externallink': "URL adresa zdroje",
            'imageurl': "URL adresa obrázku"
        }
        widgets = {
            'biographyid': forms.HiddenInput(),
            'biographytextcz': forms.Textarea(attrs={'class': 'form-control', 'rows': 20, 'style': 'height: 250px;','placeholder': 'Životopis postavy...'}),
            'externallink': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL adresa zdroje'}),
            'imageurl': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL obrázku'}),
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zdroj'}),
        }


class SearchFormCreators(forms.Form):
    q = forms.CharField(label='Hledat tvůrce', max_length=255)


class CreatorDivRatingForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = ['divrating']
        widgets = {
            'divrating': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }
        labels = {
            'divrating': 'DIV Rating (0-99)',
        }


class FavoriteForm(forms.Form):
    object_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self):
        content_type_id = 15  # Napevno pro Creator
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
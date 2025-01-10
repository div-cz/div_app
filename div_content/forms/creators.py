# forms.creators.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from div_content.models import Creator, Creatorbiography, Favorite




#class CreatorBiographyForm(forms.ModelForm):
#    ...


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
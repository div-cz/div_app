# FORMS.AUTHORS
from django import forms
from django.contrib.auth.models import User
from div_content.models import Bookcomments, Favorite, Userprofile


class SearchFormCreators(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)


class FavoriteForm(forms.Form):
    object_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self):
        content_type_id = 10  # ContentType ID pro Bookauthor
        object_id = self.cleaned_data['object_id']

        if not self.user:
            raise ValueError("Uživatel není přihlášen.")

        favorite, created = Favorite.objects.get_or_create(
            user=self.user,
            content_type_id=content_type_id,
            object_id=object_id,
        )

        if not created:
            favorite.delete() 
            return False  # Odebráno

        return True  # Přidáno


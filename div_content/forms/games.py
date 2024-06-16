# FORMS.GAMES.PY

from django import forms
from div_content.models import Game, Gamedevelopers, Gameplatform, Gamepublisher, Metacountry, Metagenre, Metauniversum

class GameForm(forms.ModelForm):
    developerid = forms.ModelChoiceField(
        queryset=Gamedevelopers.objects.all(),
        label="Developer",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="--- Vyberte ---"
    )
    platformid = forms.ModelChoiceField(
        queryset=Gameplatform.objects.all(),
        label="Platform",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="--- Vyberte ---"
    )
    publisherid = forms.ModelChoiceField(
        queryset=Gamepublisher.objects.all(),
        label="Publisher",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="--- Vyberte ---"
    )
    countryid = forms.ModelChoiceField(
        queryset=Metacountry.objects.all(),
        label="Country",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="--- Vyberte ---"
    )
    universumid = forms.ModelChoiceField(
        queryset=Metauniversum.objects.all(),
        label="Universum",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="--- Vyberte ---"
    )
    genreid = forms.ModelChoiceField(
        queryset=Metagenre.objects.all(),
        label="Genre",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="--- Vyberte ---"
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=False,
        label="Description"
    )

    class Meta:
        model = Game
        fields = ['title', 'description', 'developerid', 'platformid', 'publisherid', 'countryid', 'universumid', 'genreid']

# FORMS.GAMES.PY TEST

from django import forms
from div_content.models import Game, Gamecomments, Gamedevelopers, Gameplatform, Gamepublisher, Metacountry, Metagenre, Metaplatform,  Metauniversum


class GameDivRatingForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['divrating']
        widgets = {
            'divrating': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }
        labels = {
            'divrating': 'DIV Rating (0-99)',
        }


class GameForm(forms.ModelForm):
    developerid = forms.ModelChoiceField(
        queryset=Gamedevelopers.objects.none(),  # Nevrací nic pøi prvním naètení
        label="Developer",
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False
        #empty_label="--- Vyberte ---"
    )
    platformid = forms.ModelChoiceField(
        queryset=Metaplatform.objects.none(),  # Nevrací nic pøi prvním naètení
        label="Platform",
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False
    )
    publisherid = forms.ModelChoiceField(
        queryset=Gamepublisher.objects.none(),  # Nevrací nic pøi prvním naètení
        label="Publisher",
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False
    )
    countryid = forms.ModelChoiceField(
        queryset=Metacountry.objects.none(),
        label="Country",
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False,
    )
    universumid = forms.ModelChoiceField(
        queryset=Metauniversum.objects.none(),
        label="Universum",
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False,
    )
    genreid = forms.ModelChoiceField(
        queryset=Metagenre.objects.none(),
        label="Genre",
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=False,
        label="Description"
    )

    class Meta:
        model = Game
        fields = ['title', 'description', 'developerid', 'platformid', 'publisherid', 'countryid', 'universumid', 'genreid']








class CommentFormGame(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-100',  'style': 'height:120px'})) #bg-dark text-white 

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = Gamecomments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }




# FORMS.GAMES.PY

from django import forms
from div_content.models import Game, Gamedevelopers, Gameplatform, Gamepublisher, Metacountry, Metagenre, Metaworld

class GameForm(forms.ModelForm):
    developerid = forms.ModelChoiceField(queryset=Gamedevelopers.objects.all()[:4], label="Developer")
    platformid = forms.ModelChoiceField(queryset=Gameplatform.objects.all()[:4], label="Platform")
    publisherid = forms.ModelChoiceField(queryset=Gamepublisher.objects.all()[:4], label="Publisher")
    countryid = forms.ModelChoiceField(queryset=Metacountry.objects.all()[:4], label="Country")
    worldid = forms.ModelChoiceField(queryset=Metaworld.objects.all()[:4], label="World")
    genreid = forms.ModelChoiceField(queryset=Metagenre.objects.all()[:4], label="Genre")

    class Meta:
        model = Game
        fields = ['title', 'description', 'developerid', 'platformid', 'publisherid', 'countryid', 'worldid', 'genreid']



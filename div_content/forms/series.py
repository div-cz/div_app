# FORMS/SERIES

from django import forms
from div_content.models import Tvshow, Tvshowcomments, Tvshowtrailer


class SearchForm(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)


class TVShowDivRatingForm(forms.ModelForm):
    class Meta:
        model = Tvshow
        fields = ['divrating']
        widgets = {
            'divrating': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }
        labels = {
            'divrating': 'DIV Rating (0-9999)',
        }

# use in series/series_detail.html
class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-100',  'style': 'height:120px'})) #bg-dark text-white 

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = Tvshowcomments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

class TrailerForm(forms.ModelForm):
    class Meta:
        model = Tvshowtrailer
        fields = ['youtubeurl']

    def __init__(self, *args, **kwargs):
        super(TrailerForm, self).__init__(*args, **kwargs)
        self.fields['youtubeurl'].widget.attrs.update({'class': 'form-control'})

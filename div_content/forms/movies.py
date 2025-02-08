# FORMS.MOVIES.PY TEST

from django import forms
from django.contrib.auth.models import User
from div_content.models import Movie, Moviecinema, Moviecomments, Moviedistributor, Movieerror, Movietrailer, Userprofile


class MovieDivRatingForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['divrating']
        widgets = {
            'divrating': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }
        labels = {
            'divrating': 'DIV Rating (0-999)',
        }


# use in movies/movie_detail.html
class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-100',  'style': 'height:120px'})) #bg-dark text-white 

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = Moviecomments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class MovieCinemaForm(forms.ModelForm):
    class Meta:
        model = Moviecinema
        fields = ['distributorid', 'releasedate']

    distributorid = forms.ModelChoiceField(
        queryset=Moviedistributor.objects.all(),
        label='Distributor'
    )
    releasedate = forms.DateField(
        widget=forms.SelectDateWidget(),
        label='Datum vydání'
    )


class TrailerForm(forms.ModelForm):
    class Meta:
        model = Movietrailer
        fields = ['youtubeurl']

    def __init__(self, *args, **kwargs):
        super(TrailerForm, self).__init__(*args, **kwargs)
        self.fields['youtubeurl'].widget.attrs.update({'class': 'form-control'})


class MovieErrorForm(forms.ModelForm):
    error = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 mb-2', 'rows': 3}),
        required=True
    )
    
    class Meta:
        model = Movieerror
        fields = ['error']


# use in movie section
class SearchForm(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)

"""
# Use in profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['bio', 'profilepicture', 'birthdate', 'location']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Jméno")
    email = forms.EmailField(label="E-mail")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), label="Zpráva")
"""
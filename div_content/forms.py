from django import forms
from django.contrib.auth.models import User
from .models import Moviecomments, Userprofile

# use in movies/movie_detail.html
class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'bg-dark text-white w-100',  'style': 'height:120px'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)

    class Meta:
        model = Moviecomments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

# use in movie section
class SearchForm(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)


# Use in profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['bio', 'profilepicture', 'birthdate', 'location']

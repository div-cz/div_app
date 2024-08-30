# FORMS.ADMINS

"""

from django import forms
from div_content.models import Moviecomments

class Moviecommentform(forms.ModelForm):
    class Meta:
        model = Moviecomments
        fields = ['comment']
        labels = {
            'comment': 'Komentář',
        }
"""
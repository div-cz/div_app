# -------------------------------------------------------------------
#                    FORMS.iNDEX.PY
# -------------------------------------------------------------------

from django import forms
from div_content.models import Article, Articlenews

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'h1', 'h2', 'tagline', 'content', 'menu', 'youtube', 'img1600', 'img', 'img400x250', 'alt', 'perex', 'autor', 'typ']
        widgets = {
            'content': forms.Textarea(attrs={'id': 'summernote'}),
        }

class ArticlenewsForm(forms.ModelForm):
    class Meta:
        model = Articlenews
        fields = ['title', 'news', 'img', 'alt', 'source', 'typ'] # 'perex', 
        widgets = {
            'news': forms.Textarea(attrs={'id': 'summernote'}),
        }

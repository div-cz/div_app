# FORMS.BLOG.PY
from django import forms
from div_content.models import Articleblog, Articleblogcomment, Articleblogpost


class Articleblogcommentform(forms.ModelForm):
    class Meta:
        model = Articleblogcomment
        fields = ['content']
        labels = {
            'content': '',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Napište svůj komentář...'}),
        }


class Articleblogform(forms.ModelForm):
    class Meta:
        model = Articleblog
        fields = ['name', 'description', 'blog_type']  # Přidáme pole blog_type
        labels = {
            'name': 'Název blogu',
            'description': 'Popis blogu',
            'blog_type': 'Typ',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'blog_type': forms.RadioSelect,  # Přepínátko pro výběr typu blogu
        }


class Articleblogpostform(forms.ModelForm):
    class Meta:
        model = Articleblogpost
        fields = ['articleblog', 'title', 'content', 'category', 'tags']
        labels = {
            'articleblog': 'Vyber blog',
            'title': 'Nadpis',
            'content': 'Obsah',
            'category': 'Kategorie',
            'tags': 'Klíčová slova',
        }
        widgets = {
            'content': forms.Textarea(attrs={'id': 'summernote'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user is not None:
            user_blogs = Articleblog.objects.filter(user=user)
            self.fields['articleblog'].queryset = user_blogs
            
            # Pokud uživatel má blogy, přednastavíme první blog jako vybraný
            if user_blogs.exists():
                self.fields['articleblog'].initial = user_blogs.first()





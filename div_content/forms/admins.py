# FORMS.ADMINS.PY


from django import forms
from div_content.models import AATask, Moviecomments

class Moviecommentform(forms.ModelForm): 
    class Meta:
        model = Moviecomments
        fields = ['comment']
        labels = {
            'comment': 'Komentář',
        }




class TaskForm(forms.ModelForm):
    class Meta:
        model = AATask
        fields = ['title', 'description', 'assigned', 'status', 'priority', 'category', 'parentid', 'duedate']
        widgets = {
            'duedate': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'parentid': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Omezíme výběr parentid pouze na hlavní úkoly
        self.fields['parentid'].queryset = AATask.objects.filter(parentid__isnull=True)
        # Přidáme možnost "Nikdo" do assigned
        self.fields['assigned'].choices = [('Nikdo', 'Nikdo'), ('VendaCiki', 'VendaCiki'), 
                                         ('xsilence8x', 'xsilence8x'), ('Martin', 'Martin')]

class TaskCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Nový komentář')

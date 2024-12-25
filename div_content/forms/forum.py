from django import forms
from django.contrib.auth.models import User
from div_content.models import Forumtopic, Forumcomment
from django.utils.text import slugify
from django.urls import reverse
from django.utils.safestring import mark_safe


class ForumTopicForm(forms.ModelForm):
    first_post = forms.CharField(widget=forms.Textarea(
        attrs={"id": "summernote"}), label=""
        )

    class Meta:
        model = Forumtopic
        fields = ["title", "first_post"]
    
        labels = {
            "title": "Název příspěvku",
        }
    

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


    def clean_title(self):
        title = self.cleaned_data["title"]
        slug = slugify(title)
        if Forumtopic.objects.filter(topicurl=slug).exists():
            url = reverse("forum_topic_detail", kwargs={"slug":  "filmy","topicurl": slug})
            error_message = f"Toto téma už existuje.<br>Můžeš nad ním diskutovat zde: <a href='{url}'>{title}</a>"
            raise forms.ValidationError(mark_safe(error_message))
        return title
    

    def save(self, commit=True):
        forumtopic = super().save(commit=False)
        forumtopic.user = self.user
        # forumtopic.section = self.section
        forumtopic.topicurl = slugify(self.cleaned_data['title'])
        if commit:
            forumtopic.save()
            Forumcomment.objects.create(
                topic=forumtopic,
                user=self.user,
                body=self.cleaned_data['first_post']
            )
        return forumtopic

class ForumCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={"id": "summernote"}), label=""
        )

    class Meta:
        model = Forumcomment
        fields = ["body"]
    

class EditCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={"id": "summernote"}), label=""
        )

    class Meta:
        model = Forumcomment
        fields = ["body"]


class SearchForm(forms.Form):
    q = forms.CharField(label='Hledat', max_length=255)
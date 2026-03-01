# -------------------------------------------------------------------
#                    FORMS.LOCATION.PY
# -------------------------------------------------------------------

from django import forms
from django.utils.text import slugify
from div_content.models import Metalocation, Metatype, Metauniversum, Movielocation





class LocationCreateForm(forms.ModelForm):

    class Meta:
        model = Metalocation
        fields = [
            'locationname',
            'locationnamecz',
            'locationtypeid',
            'parentlocation',
            'universum',
            'locationdescription',
            'locationadress',
            'gpsx',
            'gpsy',
        ]

        widgets = {
            'locationname': forms.TextInput(attrs={'class': 'form-control'}),
            'locationdescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        base_slug = slugify(instance.locationname)
        slug = base_slug
        counter = 1

        while Metalocation.objects.filter(locationurl=slug).exists():
            if instance.parentlocation:
                slug = f"{base_slug}-{slugify(instance.parentlocation.locationname)}"
            else:
                slug = f"{base_slug}-{counter}"
                counter += 1

        instance.locationurl = slug

        if commit:
            instance.save()

        return instance




class LocationForm(forms.ModelForm):
    class Meta:
        model = Metalocation
        fields = [
            'locationname',
            'locationnamecz',
            'locationtypeid',
            'parentlocation',
            'universum',
            'locationdescription',
            'locationadress',
            'gpsx',
            'gpsy',
            'divrating',
        ]

        widgets = {
            'locationname': forms.TextInput(attrs={'class': 'form-control'}),
            'locationnamecz': forms.TextInput(attrs={'class': 'form-control'}),
            'locationdescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'locationadress': forms.TextInput(attrs={'class': 'form-control'}),
            'gpsx': forms.TextInput(attrs={'class': 'form-control'}),
            'gpsy': forms.TextInput(attrs={'class': 'form-control'}),
            'divrating': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    parentlocation = forms.ModelChoiceField(
        queryset=Metalocation.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    universum = forms.ModelChoiceField(
        queryset=Metauniversum.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    locationtypeid = forms.ModelChoiceField(
        queryset=Metatype.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )




class MovieLocationForm(forms.Form):
    location_name = forms.CharField(
        label="Lokace (název)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    locationrole = forms.CharField(
        label="Role (natáčeno / děj)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_location_name(self):
        name = self.cleaned_data['location_name'].strip()

        locations = Metalocation.objects.filter(locationname__iexact=name)

        if not locations.exists():
            raise forms.ValidationError("Lokace neexistuje.")

        if locations.count() > 1:
            raise forms.ValidationError("Existuje více lokalit se stejným názvem. Upřesni.")

        return locations.first()




class QuickLocationCreateForm(forms.ModelForm):

    class Meta:
        model = Metalocation
        fields = ['locationname', 'parentlocation']
        labels = {
            'locationname': 'Název lokality',
            'parentlocation': 'Nachází se v (volitelné)'
        }
        help_texts = {
            'locationname': '<i>Např. Brno nebo Liberec, Masarykova ulice nebo Pražská ulice, Česká republika</i>',
            'parentlocation': '<br><i>Např. Pražská ulice → vyberte Liberec (vždy přímý potomek ulice>město</i>)'
        }
        widgets = {
            'locationname': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        from django.utils.text import slugify
    
        name = self.cleaned_data['locationname'].strip()
    
        # 🔹 pokud existuje stejný název kdekoliv
        existing = Metalocation.objects.filter(
            locationname__iexact=name
        ).first()
    
        if existing:
            return existing
    
        instance = super().save(commit=False)
    
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
    
        while Metalocation.objects.filter(locationurl=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
    
        instance.locationurl = slug
    
        if commit:
            instance.save()
    
        return instance

# -------------------------------------------------------------------
#                    FORMS.DIVKVARIAT.PY
# -------------------------------------------------------------------

from django import forms
from div_content.models import Booklisting

class BookListingForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=10, 
        required=True, 
        initial=100,
        label='Cena',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    shipping = forms.DecimalField(
        max_digits=10, 
        required=False, 
        initial=70,
        label='Poštovné',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    personal_pickup = forms.BooleanField(
        required=False, 
        label='Osobní převzetí',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    phone = forms.CharField(
        required=False,   # <- už není povinný
        label='Telefon (volitelně)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Booklisting
        fields = ['listingtype', 'price', 'shipping', 'description', 'condition', 'location', 'personal_pickup']
        labels = {
            'listingtype': 'Typ',
            'price': 'Cena',
            'description': 'Popis',
            'condition': 'Stav',
            'location': 'Místo'
        }
        widgets = {
            'listingtype': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'style': 'height:100px !important'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        # nově přijímáme user
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.initial.get('listingtype'):
            self.initial['listingtype'] = 'SELL'
        if self.initial.get('listingtype') == 'GIVE':
            self.fields['price'].widget = forms.HiddenInput()
            self.fields['shipping'].widget = forms.HiddenInput()
            # pozor: commission tu ani není field → tohle by klidně mohlo pryč
            # self.fields['commission'].widget = forms.HiddenInput()

        # předvyplnění telefonu z profilu
        if self.user and hasattr(self.user, "userprofile") and self.user.userprofile.phone:
            self.fields['phone'].initial = self.user.userprofile.phone

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.listingtype == 'SELL':
            instance.commission = 0
        if commit:
            instance.save()

            # pokud user vyplnil telefon, ulož ho do profilu
            if self.user and self.cleaned_data.get("phone"):
                profile = getattr(self.user, "userprofile", None)
                if profile:
                    profile.phone = self.cleaned_data["phone"]
                    profile.save()
        return instance

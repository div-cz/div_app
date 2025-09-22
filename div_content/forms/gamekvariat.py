# -------------------------------------------------------------------
#                    FORMS.GAMEKVARIAT.PY
# -------------------------------------------------------------------

from django import forms
from div_content.models import Gamelisting


DEFAULT_SHIPPING = {
    "zasilkovna": 89,
    "balikovna": 99,
    "posta": 99,
}

class GameListingForm(forms.ModelForm):
    CONDITION_CHOICES = [
        ("nova", "Nová"),
        ("jako-nova", "Použitá, jako nová"),
        ("dobry", "Použitá, dobrý stav"),
        ("zachovaly", "Použitá, zachovalý stav"),
        ("spatny", "Špatný stav"),
    ]

    condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        required=False,
        label="Stav",
        initial="jako-nova",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        max_digits=10,
        required=True,
        initial=100,
        label='Cena',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    personal_pickup = forms.BooleanField(
        required=False,
        label='Osobní převzetí',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    phone = forms.CharField(
        required=False,
        label='Telefon (volitelně)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # dopravy stejné jako u knih
    shipping_zasilkovna = forms.BooleanField(required=False, label="Zásilkovna", initial=True)
    shipping_zasilkovna_price = forms.DecimalField(max_digits=6, decimal_places=0, initial=89, required=False, label="")

    shipping_balikovna = forms.BooleanField(required=False, label="Balíkovna", initial=True)
    shipping_balikovna_price = forms.DecimalField(max_digits=6, decimal_places=0, initial=99, required=False, label="")

    shipping_posta = forms.BooleanField(required=False, label="Česká pošta", initial=True)
    shipping_posta_price = forms.DecimalField(max_digits=6, decimal_places=0, initial=109, required=False, label="")

    class Meta:
        model = Gamelisting
        fields = ['listingtype', 'price', 'description', 'condition', 'location', 'personal_pickup']
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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'style': 'height:100px !important'}),
            'location': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.initial.get('listingtype'):
            self.initial['listingtype'] = 'SELL'
        if self.initial.get('listingtype') == 'GIVE':
            self.fields['price'].widget = forms.HiddenInput()

        # předvyplnění telefonu z profilu
        if self.user and hasattr(self.user, "userprofile") and self.user.userprofile.phone:
            self.fields['phone'].initial = self.user.userprofile.phone

    def save(self, commit=True):
        instance = super().save(commit=False)
        options = []
        if self.cleaned_data.get("shipping_zasilkovna"):
            options.append(f"ZASILKOVNA:{self.cleaned_data.get('shipping_zasilkovna_price') or 0}")
        if self.cleaned_data.get("shipping_balikovna"):
            options.append(f"BALIKOVNA:{self.cleaned_data.get('shipping_balikovna_price') or 0}")
        if self.cleaned_data.get("shipping_posta"):
            options.append(f"POSTA:{self.cleaned_data.get('shipping_posta_price') or 0}")

        instance.shippingoptions = ",".join(options)

        if instance.listingtype == 'SELL':
            instance.commission = 0

        if commit:
            instance.save()
            if self.user and self.cleaned_data.get("phone"):
                profile = getattr(self.user, "userprofile", None)
                if profile:
                    profile.phone = self.cleaned_data["phone"]
                    profile.save()
        return instance

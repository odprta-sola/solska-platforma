"""Obrazci zaslonov evidence (tajništvo, skrbnik)."""

from django import forms
from django.core.validators import RegexValidator

from . import models as m


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": ".csv,text/csv"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data]
        files = [f for f in files if f]
        if not files:
            raise forms.ValidationError("Izberite vsaj eno datoteko CSV.", code="required")
        return [super(MultipleFileField, self).clean(f, initial) for f in files]


class ImportForm(forms.Form):
    source = forms.CharField(
        label="Vir podatkov",
        max_length=64,
        initial="tajnistvo",
        help_text=(
            "Kratka oznaka vira (npr. tajnistvo). Isti vir pri ponovnem uvozu prepozna iste osebe."
        ),
        validators=[RegexValidator(r"^[a-z0-9-]+$", "Uporabite male črke, številke in vezaje.")],
    )
    files = MultipleFileField(
        label="Datoteke CSV",
        help_text=(
            "Ime datoteke določa vsebino, npr. persons.csv, relationships.csv. "
            "UTF-8, ločilo podpičje."
        ),
    )


class SearchForm(forms.Form):
    q = forms.CharField(label="Išči po imenu", max_length=100, required=False)


class ContactForm(forms.ModelForm):
    class Meta:
        model = m.Person
        fields = ["contact_email"]
        labels = {"contact_email": "E-naslov za obvestila"}
        help_texts = {
            "contact_email": "Prazno pomeni, da oseba nima e-naslova (papirna pot). "
            "Naslov lahko deli več oseb. Naslednji uvoz iz istega vira ga lahko spremeni."
        }

from django import forms
from .models import Utente, Link, Recensione, Tag, Libro, Autore
from django.forms import BaseModelFormSet, ValidationError, ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from dal import autocomplete

from django_select2.forms import ModelSelect2MultipleWidget


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['nome', 'link_social']
        labels = {
            'nome': 'Nome del social (Instagram, Discord, sito personale...)',
            'link_social': 'Incolla un url'
        }


LinkFormSet = modelformset_factory(Link, form=LinkForm, extra=1, can_delete=True)


class CustomUserCreationForm(UserCreationForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="I tuoi generi preferiti"
    )

    class Meta:
        model = Utente
        fields = ['username', 'email', 'password1', 'password2', 'immagine', 'tags', 'comune', 'inprovincia']
        labels = {
            "username": 'Nome utente',
            "email": 'Email',
            "immagine": 'La tua immagine profilo',
            "comune": 'Il comune in cui vuoi scambiare libri',
            "inprovincia": 'Vuoi scambiare anche in tutta la provincia?'
        }


class CreaUtenteLettore(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'username',
            'email',
            'password1',
            'password2',
            'immagine',
            'tags',
            'comune',
            'inprovincia',
        )

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name='Lettori')
        g.user_set.add(user)
        return user


class RequiredFieldsFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE", False):
                continue  # form vuoto o marcato per cancellazione => ignora

            nome = form.cleaned_data.get("nome")
            link_social = form.cleaned_data.get("link_social")

            # Se l’utente ha scritto solo uno dei due => errore
            if (nome and not link_social) or (link_social and not nome):
                raise ValidationError("Se compili un link, devi compilare anche il nome e viceversa.")


class UtenteUpdateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="I tuoi generi preferiti"
    )

    class Meta:
        model = Utente
        fields = ['username', 'immagine', 'comune', 'inprovincia', 'tags']
        labels = {
            'username': 'Nome utente',
            'immagine': 'Immagine profilo',
            'comune': 'Comune',
            'inprovincia': 'Scambi anche nella provincia'
        }


class RecensioneForm(forms.ModelForm):
    class Meta:
        model = Recensione
        fields = ['voto', 'commento']
        widgets = {
            'voto': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Invia'))


class AutoreWidget(ModelSelect2MultipleWidget):
    model = Autore
    search_fields = ["nome__icontains", "cognome__icontains"]


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titolo', 'autori', 'tags', 'trama']
        widgets = {
            'autori': autocomplete.ModelSelect2Multiple(
                url='autore-autocomplete'
            ),
            'tags': forms.CheckboxSelectMultiple(),
        }

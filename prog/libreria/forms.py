from .models import *
from django import forms
from django.forms import BaseModelFormSet, ValidationError
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from dal import autocomplete


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


"""
class AutoreWidget(ModelSelect2MultipleWidget):
    model = Autore
    search_fields = ["nome__icontains", "cognome__icontains"]  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


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


class EventoForm(forms.ModelForm):
    via = forms.CharField(max_length=50, label="Via")
    comune = forms.ModelChoiceField(queryset=Comune.objects.all(), label="Comune")

    class Meta:
        model = Evento
        fields = ["idlibro", "date", "descrizione", "via", "comune"]
        labels = {
            'idlibro': "Il titolo del libro",
            'date': "La data dell'evento",
            'descrizione': "Lascia una tua nota per i lettori",
            'via': "La via",
            'comune': "Seleziona un comune",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "descrizione": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        # Filtro i libri: solo quelli dell'autore collegato all'utente
        if getattr(user, "autore_id", None):
            self.fields["idlibro"].queryset = (
                Libro.objects.filter(autori=user.autore).order_by("titolo")
            )
        else:
            # Utente senza autore collegato: nessun libro selezionabile => Non dovrebbe mai verificarsi
            self.fields["idlibro"].queryset = Libro.objects.none()

    def save(self, commit=True):
        evento = super().save(commit=False)

        via = self.cleaned_data["via"].strip()
        comune = self.cleaned_data["comune"]
        luogo, _ = Luogo.objects.get_or_create(via=via, comune=comune)

        evento.luogo = luogo
        if commit:
            evento.save()
        return evento


class EventiFilterForm(forms.Form):
    provincia = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Province disponibili
        province = Luogo.objects.values_list('comune__provincia', flat=True).filter(evento__date__gte=timezone.now()).distinct()
        self.fields['provincia'].choices = [('', 'Tutte')] + [(p, p) for p in province]

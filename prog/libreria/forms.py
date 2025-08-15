from django import forms
from .models import Utente, Link
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model


class UtenteCrispyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # perché il form principale sarà fuori
        self.helper.disable_csrf = True

    class Meta:
        model = Utente
        fields = ['username', 'password', 'email', 'immagine', 'comune', 'inprovincia', 'tags']


LinkFormSet = modelformset_factory(
    Link,
    fields=['nome', 'link_social'],
    extra=2,
    can_delete=True
)


class UtenteForm(forms.ModelForm):
    class Meta:
        model = Utente
        fields = ['username', 'password', 'email', 'immagine', 'comune', 'inprovincia', 'tags']
        widgets = {
            'password': forms.PasswordInput(),
            'tags': forms.CheckboxSelectMultiple(),
        }


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['nome', 'link_social']
        labels = {
            'nome': 'Nome del link (es. Instagram, sito personale...)',
            'link_social': 'URL'
        }


# LinkFormSet = forms.modelformset_factory(Link, form=LinkForm, extra=3, can_delete=True)

user = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = user
        fields = ['username', 'email', 'password1', 'password2', 'tags']


class CreaUtenteLettore(CustomUserCreationForm):

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name='Lettori')
        g.user_set.add(user)
        return user

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from libreria.models import *
from libreria.forms import *


def home(request):
    categorie = []
    for tag in Tag.objects.all():
        libri = tag.libro_set.all()[:4]  # primi 4 libri
        if libri.exists():
            categorie.append({
                'id': tag.id,
                'nome': tag.nome,
                'libri': libri
            })

    ctx = {
        "title": "HomeDiAnnaB",
        "categorie": categorie
    }

    return render(request, template_name="hometemplate.html", context=ctx)


def risultati_ricerca(request):
    query = request.GET.get('search', '').strip()

    libri = Libro.objects.filter(titolo__icontains=query)
    autori = Autore.objects.filter(nome__icontains=query)

    return render(request, 'risultati_ricerca.html', {
        'query': query,
        'libri': libri,
        'autori': autori
    })


class UserCreateView(CreateView):
    form_class = CreaUtenteLettore
    template_name = "user_create.html"
    success_url = reverse_lazy('login')

def register(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST, request.FILES)
        formset = LinkFormSet(request.POST, queryset=Link.objects.none())

        if user_form.is_valid() and formset.is_valid():
            user = user_form.save()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    nome = form.cleaned_data.get("nome")
                    link_social = form.cleaned_data.get("link_social")
                    if nome and link_social:
                        link = form.save(commit=False)
                        link.utente = user
                        link.save()

            messages.success(request, "Registrazione completata con successo!")
            # login(request, user)  # login automatico dopo la registrazione
            return redirect("login")
    else:
        user_form = CustomUserCreationForm()
        formset = LinkFormSet(queryset=Link.objects.none())

    return render(request, "user_create.html", {
        "user_form": user_form,
        "formset": formset
    })


def libri_categoria_detail(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    libri = tag.libro_set.all()
    return render(request, 'libri_categoria_detail.html', {
        'tag': tag,
        'libri': libri
    })


# Da togliere!!!
@login_required
def my_situation(request):
    user = get_object_or_404(Utente, pk=request.user.pk)
    name = user.username
    ctx = {"title":  name}
    return render(request,"pstatic.html", ctx)


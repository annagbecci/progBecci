from libreria.forms import *
from django.views.generic import CreateView, ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django_select2.forms import ModelSelect2MultipleWidget
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from dal import autocomplete

User = get_user_model()


def home(request):
    scrittori = User.objects.filter(groups__name="Autori")

    categorie = []
    for tag in Tag.objects.all().order_by("nome"):
        libri = tag.libro_set.all().order_by("-mediavoti")[:3]  # primi 3 libri: CAMBIARE ORDINE
        if libri.exists():
            categorie.append({
                'id': tag.id,
                'nome': tag.nome,
                'libri': libri
            })

    interessi = []
    if request.user.is_authenticated:
        letti = Libro.objects.filter(recensioni__nomeutente=request.user)

        for tag in request.user.tags.all():
            libri = tag.libro_set.exclude(id__in=letti).order_by("-mediavoti")[:3]
            if libri.exists():
                interessi.append({
                    'id': tag.id,
                    'nome': tag.nome,
                    'libri': libri
                })


    ctx = {
        "autori": scrittori,
        "title": "Home page",
        "categorie": categorie,
        "interessi": interessi
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
                        link.save()
                        user.links.add(link)

            messages.success(request, "Registrazione completata con successo!")
            return redirect("login")
    else:
        user_form = CustomUserCreationForm()
        formset = LinkFormSet(queryset=Link.objects.none())

    return render(request, "user_create.html", {
        "user_form": user_form,
        "formset": formset
    })


@login_required
def update_utente(request):
    utente = Utente.objects.get(pk=request.user.pk)

    if request.method == "POST":
        form = UtenteUpdateForm(request.POST, request.FILES, instance=utente)
        formset = LinkFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            form.save()
            links = formset.save()
            for link in links:
                utente.links.add(link)

            messages.success(request, "Profilo aggiornato con successo!")
            return redirect("libreria:utente_detail")
        else:
            messages.error(request, "Ci sono errori, controlla i campi.")

    else:
        formset = LinkFormSet(queryset=utente.links.all())
        form = UtenteUpdateForm(instance=utente)

    return render(request, "libreria/utente_update.html", {
        "form": form,
        "formset": formset,
    })


def libri_categoria_detail(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    libri = tag.libro_set.all()
    return render(request, 'libri_categoria_detail.html', {
        'tag': tag,
        'libri': libri
    })


class AutoreCreateView(LoginRequiredMixin, CreateView):
    model = Autore
    fields = ['nome', 'biografia']
    template_name = 'autore_create.html'

    def get_success_url(self):
        return reverse_lazy('risultati_ricerca')


class AutoreAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Autore.objects.none()

        qs = Autore.objects.all()

        if self.q:
            qs = qs.filter(nome__icontains=self.q)

        return qs


class AutoreWidget(ModelSelect2MultipleWidget):  # DOVREI AGGIUNGERE UN CONTROLLO SULL'ACCESSO
    model = Autore
    search_fields = ["nome__icontains"]


class LibroCreateView(LoginRequiredMixin, CreateView):
    model = Libro
    form_class = LibroForm
    template_name = 'libro_add.html'

    def get_success_url(self):
        return reverse_lazy('risultati_ricerca')


class EventoCreateView(GroupRequiredMixin, CreateView):
    group_required = ["Autori"]
    form_class = EventoForm
    template_name = "evento_create.html"
    success_url = reverse_lazy("eventi_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.autore = self.request.user
        return super().form_valid(form)


class EventiList(LoginRequiredMixin, ListView):
    model = Evento
    template_name = 'eventi_list.html'
    context_object_name = 'eventi'

    def get_queryset(self):
        qs = Evento.objects.filter(date__gte=timezone.now()).order_by("date")
        form = EventiFilterForm(self.request.GET)

        if form.is_valid():
            provincia = form.cleaned_data.get('provincia')
            if provincia:
                qs = qs.filter(luogo__comune__provincia=provincia)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = EventiFilterForm(self.request.GET)
        return context

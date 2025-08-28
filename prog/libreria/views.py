from libreria.models import *
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.decorators import login_required
from braces.views import LoginRequiredMixin, GroupRequiredMixin


@login_required
def index(request):
    user = get_object_or_404(Utente, pk=request.user.pk)
    title = "Libreria di " + user.username

    recensioni_utente = Recensione.objects.filter(nomeutente=user)

    ctx = {
        "title": title,
        "recensioni": recensioni_utente.order_by("data_aggiunta").reverse(),
    }
    return render(request, "libreria/libwelcome.html", ctx)


class UtenteDetail(LoginRequiredMixin, DetailView):
    model = Utente
    template_name = 'libreria/utente_detail.html'
    context_object_name = 'utente'

    def get_object(self, **kwargs):
        return self.request.user


class UtenteList(ListView):
    model = Utente
    template_name = 'libreria/utente_list.html'


class AutoreList(ListView):
    model = Autore
    template_name = 'libreria/autore_list.html'


class AutoreDetail(DetailView):
    model = Autore
    template_name = 'libreria/autore_detail.html'


class LibroDetail(DetailView):
    model = Libro
    template_name = 'libreria/libro_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        libro = self.object
        recensioni = libro.recensioni.filter(commento__isnull=False).exclude(commento="")
        context["recensioni"] = recensioni.order_by("data_aggiunta").reverse

        if self.request.user.is_authenticated:
            context["in_lista_desideri"] = ListaDesideri.objects.filter(
                idlibro=self.object,
                nomeutente=self.request.user
            ).exists()
        else:
            context["in_lista_desideri"] = False

        if self.request.user.is_authenticated:
            context["in_lista_scambio"] = ListaScambio.objects.filter(
                idlibro=self.object,
                nomeutente=self.request.user
            ).exists()
        else:
            context["in_lista_scambio"] = False

        return context


class RecensioneCreate(LoginRequiredMixin, CreateView):
    model = Recensione
    form_class = RecensioneForm
    template_name = 'libreria/recensione_form.html'

    def form_valid(self, form):
        form.instance.nomeutente = self.request.user
        libro = Libro.objects.get(pk=self.kwargs['pk'])
        form.instance.idlibro = libro
        response = super().form_valid(form)

        libro.aggiorna_valutazione(form.instance.voto)

        return response

    def get_success_url(self):
        return reverse_lazy('libreria:libro_detail', kwargs={'pk': self.kwargs['pk']})


@login_required
def modifica_lista_desideri(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    utente = request.user

    obj = ListaDesideri.objects.filter(idlibro=libro, nomeutente=utente).first()
    if obj:
        obj.delete()
        messages.info(request, "Libro rimosso dalla lista desideri.", extra_tags="ld")
    else:
        ListaDesideri.objects.create(idlibro=libro, nomeutente=utente)
        messages.success(request, "Libro aggiunto alla lista desideri!", extra_tags="ld")

    return redirect('libreria:libro_detail', pk=pk)


class ListaDesideriListView(LoginRequiredMixin, ListView):
    model = ListaDesideri
    template_name = "libreria/listadesideri.html"
    context_object_name = 'libri'

    def get_queryset(self):
        return ListaDesideri.objects.filter(nomeutente=self.request.user).select_related('idlibro')


@login_required
def modifica_lista_scambio(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    utente = request.user

    obj = ListaScambio.objects.filter(idlibro=libro, nomeutente=utente).first()
    if obj:
        obj.delete()
        messages.info(request, "Libro rimosso dalla lista dei libri che vuoi scambiare.", extra_tags="ls")
    else:
        ListaScambio.objects.create(idlibro=libro, nomeutente=utente)
        messages.success(request, "Libro aggiunto alla lista di libri da scambiare!", extra_tags="ls")

    return redirect('libreria:libro_detail', pk=pk)


class ListaScambioListView(LoginRequiredMixin, ListView):
    model = ListaScambio
    template_name = "libreria/listascambio.html"
    context_object_name = 'libri'

    def get_queryset(self):
        return ListaScambio.objects.filter(nomeutente=self.request.user).select_related('idlibro')


class NoteListView(LoginRequiredMixin, ListView):
    model = Nota
    template_name = "libreria/nota_list.html"
    context_object_name = "note"

    def get_queryset(self):
        libro_id = self.kwargs['pk']
        return Nota.objects.filter(
            nomeutente=self.request.user,
            idlibro_id=libro_id
        ).select_related('idlibro')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["libro"] = Libro.objects.get(pk=self.kwargs['pk'])
        return context


class NotaCreateView(LoginRequiredMixin, CreateView):
    model = Nota
    fields = ['messaggio']
    template_name = "libreria/nota_form.html"

    def form_valid(self, form):
        form.instance.nomeutente = self.request.user
        libro = get_object_or_404(Libro, pk=self.kwargs['pk'])
        form.instance.idlibro = libro
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('libreria:note_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["libro"] = Libro.objects.get(pk=self.kwargs['pk'])
        return context


class LibroScambioListView(LoginRequiredMixin, ListView):
    model = ListaScambio
    template_name = "libreria/scambi_libro.html"
    context_object_name = "scambi"

    def get_queryset(self):
        libro_id = self.kwargs['pk']
        return (ListaScambio.objects.filter(idlibro_id=libro_id).select_related('idlibro')
                .exclude(nomeutente=self.request.user)
                .exclude(nomeutente__comune=None)
                .exclude(nomeutente__links=None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context["scambi"]

        stessa_provincia = []
        altra_provincia = []

        user_comune = getattr(self.request.user, "comune", None)

        for scambio in queryset:
            if user_comune and (scambio.nomeutente.comune.provincia == user_comune.provincia):
                """se l'utente che cerca ha impostato il comune, divido gli scambiatori disponibili tra quelli vicino a
                lui (quelli nella stessa provincia, indipendentemente dalla scelta di scambiare anche nella provincia)
                e quelli fuori provincia => poi viene scritto su schermo dove è disposto a scambiare di preciso"""
                stessa_provincia.append(scambio)
            else:
                """se l'utente che cerca NON ha impostato il comune, tutti gli scambiatori saranno allo stesso livello, 
                senza distinzione di lontananza"""
                altra_provincia.append(scambio)

        context["stessa_provincia"] = stessa_provincia
        context["altra_provincia"] = altra_provincia

        return context


class ScambiatorePage(LoginRequiredMixin, ListView):
    model = ListaScambio
    template_name = "libreria/scambiatore_page.html"
    context_object_name = "disponibili"

    def get_queryset(self):
        return ListaScambio.objects.filter(nomeutente_id=self.kwargs['pk']).select_related("idlibro")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["utente"] = Utente.objects.get(pk=self.kwargs['pk'])
        return context


class EventoCreateView(GroupRequiredMixin, CreateView):
    group_required = ["Autori"]
    form_class = EventoForm
    template_name = "libreria/evento_create.html"
    success_url = reverse_lazy("home_page")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.autore = self.request.user
        return super().form_valid(form)

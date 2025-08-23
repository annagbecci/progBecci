from libreria.models import *
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.decorators import login_required
from braces.views import LoginRequiredMixin


@login_required
def index(request):
    user = get_object_or_404(Utente, pk=request.user.pk)
    title = "Libreria di " + user.username
    ctx = {"title":  title}
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

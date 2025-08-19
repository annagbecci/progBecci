from braces.views import LoginRequiredMixin

from libreria.models import *
from .forms import *
from django.views import View
from django.views.generic import DetailView, ListView, CreateView

# from .forms import UtenteCrispyForm, LinkFormSet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q


@login_required
def index(request):
    user = get_object_or_404(Utente, pk=request.user.pk)
    title = "Libreria di " + user.username
    ctx = {"title":  title}
    return render(request, "libreria/libwelcome.html", ctx)


"""
class UtenteCrispyCreateView(View):
    # Uso View e non CreateView perché devo gestire più form (utente + link) insieme.
    def get(self, request):  # mostra il form vuoto
        utente_form = UtenteCrispyForm()
        link_formset = LinkFormSet(queryset=Link.objects.none())
        return render(request, "libreria/utente_crispyform.html", {
            "utente_form": utente_form,
            "link_formset": link_formset
        })

    def post(self, request):  # gestisce l'invio del form
        utente_form = UtenteCrispyForm(request.POST)  # ricrea il form utente con i dati inviati dal browser.
        link_formset = LinkFormSet(request.POST)

        if utente_form.is_valid() and link_formset.is_valid():
            utente = utente_form.save()
            links = link_formset.save(commit=False)  # aspetto che ci sia l'istanza di utente per creare quelle dei link
            for link in links:
                link.utente = utente
                link.save()
            return redirect("libreria:utente_list")

        return render(request, "libreria/utente_crispyform.html", {
            # se il form non è valido ricarica la pagina (evidenziando gli errori (lo fa django con i form))
            "utente_form": utente_form,
            "link_formset": link_formset
        })
"""


class UtenteDetail(DetailView):
    model = Utente
    template_name = 'libreria/utente_detail.html'


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
        context["recensioni"] = recensioni
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

from django.contrib import admin
from .models import (Utente, Tag, Comune, Link, Autore, Libro, Recensione,
                     Nota, ListaDesideri, ListaScambio, Luogo, Evento)

admin.site.register(Utente)
admin.site.register(Tag)
admin.site.register(Comune)
admin.site.register(Link)
admin.site.register(Autore)
admin.site.register(Libro)
admin.site.register(Recensione)
admin.site.register(Nota)
admin.site.register(ListaDesideri)
admin.site.register(ListaScambio)
admin.site.register(Luogo)
admin.site.register(Evento)

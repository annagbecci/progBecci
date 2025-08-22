from django.urls import path
from . import views

app_name = 'libreria'

urlpatterns = [
    path('', views.index, name='index'),
    path('utente/<int:pk>/', views.UtenteDetail.as_view(), name='utente_detail'),
    path('utente-list/', views.UtenteList.as_view(), name='utente_list'),
    path('autore-list/', views.AutoreList.as_view(), name='autore_list'),
    path('autore/<int:pk>/', views.AutoreDetail.as_view(), name='autore_detail'),
    path('libro/<int:pk>/', views.LibroDetail.as_view(), name='libro_detail'),
    path('libro/<int:pk>/recensione/', views.RecensioneCreate.as_view(), name="nuova_recensione"),
    path('lista-desideri/aggiungi/<int:pk>/', views.modifica_lista_desideri, name='modifica_ld'),
    path('lista-desideri/', views.ListaDesideriListView.as_view(), name='lista_desideri'),
    path('lista-scambio/aggiungi/<int:pk>/', views.modifica_lista_scambio, name='modifica_ls'),
    path('lista-scambio/', views.ListaScambioListView.as_view(), name='lista_scambio'),
    # path('utente-createcrispy/', views.UtenteCrispyCreateView.as_view(), name='utente_crispycreate'),
    # path('utente-update/<int:pk>/', views.UtenteUpdate.as_view(), name='utente_update'),
    # path('utente-delete/<int:pk>/', views.UtenteDelete.as_view(), name='utente_delete'),
]

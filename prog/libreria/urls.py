from django.urls import path
from . import views

app_name = 'libreria'

urlpatterns = [
    path('', views.index, name='index'),
    path('utente/<int:pk>/', views.UtenteDetail.as_view(), name='libreria_detail'),
    path('utente-list/', views.UtenteList.as_view(), name='utente_list'),
    path('autore-list/', views.AutoreList.as_view(), name='autore_list'),
    path('utente-createcrispy/', views.UtenteCrispyCreateView.as_view(), name='utente_crispycreate'),
    # path('utente-update/<int:pk>/', views.UtenteUpdate.as_view(), name='utente_update'),
    # path('utente-delete/<int:pk>/', views.UtenteDelete.as_view(), name='utente_delete'),
]

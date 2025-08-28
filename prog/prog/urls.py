from django.contrib import admin
from django.urls import path, re_path, include
from . import views
from .views import *
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^$|^/$|^home/$", home, name="home_page"),
    path("libreria/", include('libreria.urls')),
    path("cerca/", views.risultati_ricerca, name="risultati_ricerca"),
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('utente-update/', update_utente, name='utente_update'),
    path("libri-categoria/<int:tag_id>/", views.libri_categoria_detail, name="libri_categoria_detail"),
    path("autore-crea/", views.AutoreCreateView.as_view(), name="autore_create"),
    path("autore-autocomplete/", AutoreAutocomplete.as_view(), name="autore-autocomplete"),
    path("select2/", include("django_select2.urls")),
    path("libro-crea/", views.LibroCreateView.as_view(), name="libro_create"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

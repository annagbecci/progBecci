"""
URL configuration for prog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path("cerca/", views.risultati_ricerca, name="risultati_ricerca"),
    path("situation/", my_situation, name='stat'),  # Questo è da togliere
    path("libreria/", include('libreria.urls')),
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('utente-update/', update_utente, name='utente_update'),
    path("libri-categoria/<int:tag_id>/", views.libri_categoria_detail, name="libri_categoria_detail"),
    path("autore-crea/", views.AutoreCreateView.as_view(), name="autore_create"),
    path(
        "autore-autocomplete/",
        AutoreAutocomplete.as_view(),
        name="autore-autocomplete",
    ),
    path("select2/", include("django_select2.urls")),
    path("libro-crea/", views.LibroCreateView.as_view(), name="libro_create"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

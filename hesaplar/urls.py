from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import GirisFormu

urlpatterns = [
    path("", views.ana_sayfa, name="ana_sayfa"),
    path(
        "giris/",
        auth_views.LoginView.as_view(
            template_name="hesaplar/giris.html", authentication_form=GirisFormu, redirect_authenticated_user=True
        ),
        name="giris",
    ),
    path("cikis/", auth_views.LogoutView.as_view(), name="cikis"),
    path("sifre/", views.sifre_degistir, name="sifre_degistir"),
    # Admin paneli
    path("panel/", views.panel, name="panel"),
    path("panel/kisiler/", views.kisi_listesi, name="kisi_listesi"),
    path("panel/kisiler/yeni/", views.kisi_ekle, name="kisi_ekle"),
    path("panel/kisiler/<int:pk>/", views.kisi_duzenle, name="kisi_duzenle"),
    path("panel/kisiler/<int:pk>/sifre/", views.kisi_sifre, name="kisi_sifre"),
    path("panel/gorevler/", views.pozisyon_listesi, name="pozisyon_listesi"),
    path("panel/gorevler/yeni/", views.pozisyon_ekle, name="pozisyon_ekle"),
    path("panel/gorevler/<int:pk>/", views.pozisyon_duzenle, name="pozisyon_duzenle"),
    path("panel/atolyeler/", views.atolye_listesi, name="atolye_listesi"),
    path("panel/atolyeler/yeni/", views.atolye_ekle, name="atolye_ekle"),
    path("panel/atolyeler/<int:pk>/", views.atolye_duzenle, name="atolye_duzenle"),
]

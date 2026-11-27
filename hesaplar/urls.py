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
    path("kullanicilar/", views.kullanici_listesi, name="kullanici_listesi"),
    path("kullanicilar/yeni/", views.kullanici_ekle, name="kullanici_ekle"),
    path("kullanicilar/<int:pk>/", views.kullanici_duzenle, name="kullanici_duzenle"),
    path("kullanicilar/<int:pk>/sifre/", views.kullanici_sifre_sifirla, name="kullanici_sifre_sifirla"),
]

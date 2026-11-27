from django.urls import path

from . import views

urlpatterns = [
    path("", views.defter, name="defter"),
    path("yeni/", views.kayit_ekle, name="kayit_ekle"),
    path("<int:pk>/", views.kayit_duzenle, name="kayit_duzenle"),
    path("<int:pk>/kapat/", views.kayit_kapat, name="kayit_kapat"),
]

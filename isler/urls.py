from django.urls import path

from . import views

urlpatterns = [
    path("", views.liste, name="is_listesi"),
    path("yeni/", views.yeni, name="is_yeni"),
    path("<int:pk>/", views.detay, name="is_detay"),
    path("<int:pk>/duzenle/", views.duzenle, name="is_duzenle"),
    path("<int:pk>/islem/", views.islem, name="is_islem"),
    path("bildirimler/", views.bildirimler, name="bildirimler"),
    path("bildirimler/durum/", views.bildirim_durumu, name="bildirim_durumu"),
]

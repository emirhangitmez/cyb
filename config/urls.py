from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Vardiya Takip Yönetimi"
admin.site.site_title = "Vardiya Takip"

urlpatterns = [
    path("yonetim/", admin.site.urls),
    path("", include("hesaplar.urls")),
]

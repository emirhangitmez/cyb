from django.contrib import admin

from .models import ArizaKaydi


@admin.register(ArizaKaydi)
class ArizaKaydiAdmin(admin.ModelAdmin):
    list_display = ("tarih", "vardiya", "atolye", "postabasi", "ekipman", "durum")
    list_filter = ("atolye", "durum", "vardiya", "tarih")
    search_fields = ("ekipman", "ariza", "yapilan_is", "notlar")

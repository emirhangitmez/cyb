from django.contrib import admin

from .models import Bildirim, Hareket, Is


class HareketInline(admin.TabularInline):
    model = Hareket
    extra = 0


@admin.register(Is)
class IsAdmin(admin.ModelAdmin):
    list_display = ("baslik", "atolye", "sorumlu", "durum", "oncelik", "son_tarih")
    list_filter = ("durum", "atolye", "oncelik")
    search_fields = ("baslik", "aciklama", "ekipman")
    inlines = [HareketInline]


admin.site.register(Bildirim)

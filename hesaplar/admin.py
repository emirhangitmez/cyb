from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Atolye, Kullanici, Pozisyon


@admin.register(Kullanici)
class KullaniciAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "pozisyon", "atolye", "is_active")
    list_filter = ("pozisyon", "atolye", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Fabrika bilgileri", {"fields": ("pozisyon", "atolye", "sicil_no", "telefon")}),)


admin.site.register(Atolye)
admin.site.register(Pozisyon)

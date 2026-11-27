from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Kullanici


@admin.register(Kullanici)
class KullaniciAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "rol", "atolye", "is_active")
    list_filter = ("rol", "atolye", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Fabrika bilgileri", {"fields": ("rol", "atolye", "sicil_no", "telefon")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Fabrika bilgileri", {"fields": ("rol", "atolye")}),)

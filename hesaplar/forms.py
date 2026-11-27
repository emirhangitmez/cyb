from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm

from .models import Kullanici, Rol


class GirisFormu(AuthenticationForm):
    error_messages = {
        "invalid_login": "Kullanıcı adı veya şifre hatalı.",
        "inactive": "Bu hesap pasif durumda. Müdürünüzle görüşün.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Kullanıcı adı"
        self.fields["password"].label = "Şifre"
        self.fields["username"].widget.attrs.update({"autofocus": True, "autocomplete": "username"})


class KullaniciFormuTemel(forms.ModelForm):
    class Meta:
        model = Kullanici
        fields = ["username", "first_name", "last_name", "rol", "atolye", "sicil_no", "telefon", "is_active"]
        labels = {
            "username": "Kullanıcı adı",
            "first_name": "Ad",
            "last_name": "Soyad",
            "is_active": "Aktif (giriş yapabilir)",
        }
        help_texts = {"username": "Giriş için kullanılır. Türkçe karakter ve boşluk kullanmayın (ör. ahmet.yilmaz)."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["atolye"].choices = [("", "Tüm atölyeler (sadece müdür/mühendis)")] + list(
            self.fields["atolye"].choices
        )[1:]
        self.fields["is_active"].help_text = "İşten ayrılanları silmek yerine pasif yapın; geçmiş kayıtları korunur."

    def clean(self):
        veri = super().clean()
        rol, atolye = veri.get("rol"), veri.get("atolye")
        if rol in (Rol.FORMEN, Rol.PERSONEL) and not atolye:
            self.add_error("atolye", "Formen ve personel için atölye seçilmelidir.")
        return veri


class KullaniciEklemeFormu(KullaniciFormuTemel):
    sifre1 = forms.CharField(label="Şifre", widget=forms.PasswordInput, min_length=6)
    sifre2 = forms.CharField(label="Şifre (tekrar)", widget=forms.PasswordInput)

    def clean(self):
        veri = super().clean()
        if veri.get("sifre1") and veri.get("sifre1") != veri.get("sifre2"):
            self.add_error("sifre2", "Şifreler aynı değil.")
        return veri

    def save(self, commit=True):
        kullanici = super().save(commit=False)
        kullanici.set_password(self.cleaned_data["sifre1"])
        if commit:
            kullanici.save()
        return kullanici


class SifreBelirlemeFormu(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Yeni şifre"
        self.fields["new_password2"].label = "Yeni şifre (tekrar)"
        self.fields["new_password1"].help_text = ""

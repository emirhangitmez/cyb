from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm

from .models import Atolye, Kullanici, Pozisyon


class GirisFormu(AuthenticationForm):
    error_messages = {
        "invalid_login": "Kullanıcı adı veya şifre hatalı.",
        "inactive": "Bu hesap pasif durumda. Yöneticinizle görüşün.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Kullanıcı adı"
        self.fields["password"].label = "Şifre"
        self.fields["username"].widget.attrs.update({"autofocus": True, "autocomplete": "username"})


class KisiFormu(forms.ModelForm):
    class Meta:
        model = Kullanici
        fields = ["first_name", "last_name", "username", "pozisyon", "atolye", "sicil_no", "telefon", "is_active", "is_staff"]
        labels = {
            "username": "Kullanıcı adı (giriş ID)",
            "first_name": "Ad",
            "last_name": "Soyad",
            "is_active": "Aktif (giriş yapabilir)",
            "is_staff": "Admin (bu paneli kullanabilir)",
        }
        help_texts = {
            "username": "Girişte kullanılır. Türkçe karakter ve boşluk kullanmayın (ör. ahmet.yilmaz).",
            "is_active": "İşten ayrılanları silmek yerine pasif yapın; geçmiş kayıtları korunur.",
            "is_staff": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["pozisyon"].queryset = Pozisyon.objects.filter(aktif=True)
        self.fields["pozisyon"].empty_label = "Seçiniz"
        self.fields["atolye"].queryset = Atolye.objects.filter(aktif=True)
        self.fields["atolye"].empty_label = "Atölye yok / tüm atölyeler"

    def clean(self):
        veri = super().clean()
        pozisyon, atolye = veri.get("pozisyon"), veri.get("atolye")
        if pozisyon and pozisyon.atolye_gerekli and not atolye:
            self.add_error("atolye", f"{pozisyon} görevi için atölye seçilmelidir.")
        if not pozisyon and not veri.get("is_staff"):
            self.add_error("pozisyon", "Bir görev seçin (sadece admin hesapları görevsiz olabilir).")
        return veri


class KisiEklemeFormu(KisiFormu):
    sifre1 = forms.CharField(label="Şifre", widget=forms.PasswordInput, min_length=6)
    sifre2 = forms.CharField(label="Şifre (tekrar)", widget=forms.PasswordInput)

    def clean(self):
        veri = super().clean()
        if veri.get("sifre1") and veri.get("sifre1") != veri.get("sifre2"):
            self.add_error("sifre2", "Şifreler aynı değil.")
        return veri

    def save(self, commit=True):
        kisi = super().save(commit=False)
        kisi.set_password(self.cleaned_data["sifre1"])
        if commit:
            kisi.save()
        return kisi


class PozisyonFormu(forms.ModelForm):
    class Meta:
        model = Pozisyon
        fields = ["ad", "yetki", "atolye_gerekli", "sira", "aktif"]


class AtolyeFormu(forms.ModelForm):
    class Meta:
        model = Atolye
        fields = ["ad", "kod", "aciklama", "aktif"]


class SifreBelirlemeFormu(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Yeni şifre"
        self.fields["new_password2"].label = "Yeni şifre (tekrar)"
        self.fields["new_password1"].help_text = ""

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import KullaniciEklemeFormu, KullaniciFormuTemel, SifreBelirlemeFormu
from .models import Kullanici, Rol
from .yetki import rol_gerekli


@login_required
def ana_sayfa(request):
    return render(request, "hesaplar/ana_sayfa.html")


@rol_gerekli(Rol.MUDUR)
def kullanici_listesi(request):
    kullanicilar = Kullanici.objects.all().order_by("-is_active", "atolye", "rol", "first_name")
    return render(request, "hesaplar/kullanici_listesi.html", {"kullanicilar": kullanicilar})


@rol_gerekli(Rol.MUDUR)
def kullanici_ekle(request):
    form = KullaniciEklemeFormu(request.POST or None)
    if request.method == "POST" and form.is_valid():
        k = form.save()
        messages.success(request, f"{k} eklendi.")
        return redirect("kullanici_listesi")
    return render(request, "hesaplar/kullanici_formu.html", {"form": form, "baslik": "Yeni kullanıcı"})


@rol_gerekli(Rol.MUDUR)
def kullanici_duzenle(request, pk):
    kullanici = get_object_or_404(Kullanici, pk=pk)
    form = KullaniciFormuTemel(request.POST or None, instance=kullanici)
    if request.method == "POST" and form.is_valid():
        if kullanici == request.user and not form.cleaned_data["is_active"]:
            form.add_error("is_active", "Kendi hesabınızı pasif yapamazsınız.")
        else:
            form.save()
            messages.success(request, f"{kullanici} güncellendi.")
            return redirect("kullanici_listesi")
    return render(
        request,
        "hesaplar/kullanici_formu.html",
        {"form": form, "baslik": f"{kullanici} düzenle", "kullanici": kullanici},
    )


@rol_gerekli(Rol.MUDUR)
def kullanici_sifre_sifirla(request, pk):
    kullanici = get_object_or_404(Kullanici, pk=pk)
    form = SifreBelirlemeFormu(kullanici, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{kullanici} için yeni şifre belirlendi.")
        return redirect("kullanici_listesi")
    return render(
        request,
        "hesaplar/kullanici_formu.html",
        {"form": form, "baslik": f"{kullanici} için yeni şifre"},
    )


@login_required
def sifre_degistir(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    form.fields["old_password"].label = "Mevcut şifre"
    form.fields["new_password1"].label = "Yeni şifre"
    form.fields["new_password1"].help_text = ""
    form.fields["new_password2"].label = "Yeni şifre (tekrar)"
    if request.method == "POST" and form.is_valid():
        kullanici = form.save()
        update_session_auth_hash(request, kullanici)
        messages.success(request, "Şifreniz değiştirildi.")
        return redirect("ana_sayfa")
    return render(request, "hesaplar/kullanici_formu.html", {"form": form, "baslik": "Şifremi değiştir"})

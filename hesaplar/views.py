from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AtolyeFormu, KisiEklemeFormu, KisiFormu, PozisyonFormu, SifreBelirlemeFormu
from .models import Atolye, Kullanici, Pozisyon
from .yetki import admin_gerekli


@login_required
def ana_sayfa(request):
    return render(request, "hesaplar/ana_sayfa.html")


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
    return render(request, "form_sayfasi.html", {"form": form, "baslik": "Şifremi değiştir", "geri": "ana_sayfa"})


# ---------------- Admin paneli ----------------

@admin_gerekli
def panel(request):
    return render(
        request,
        "panel/ozet.html",
        {
            "kisi_sayisi": Kullanici.objects.filter(is_active=True).count(),
            "pozisyonlar": Pozisyon.objects.annotate(sayi=Count("kisiler")),
            "atolyeler": Atolye.objects.annotate(sayi=Count("kisiler")),
            "gorevsizler": Kullanici.objects.filter(pozisyon__isnull=True, is_staff=False, is_superuser=False),
        },
    )


@admin_gerekli
def kisi_listesi(request):
    kisiler = Kullanici.objects.select_related("pozisyon", "atolye").order_by(
        "-is_active", "atolye__ad", "pozisyon__sira", "first_name"
    )
    atolye = request.GET.get("atolye")
    pozisyon = request.GET.get("gorev")
    if atolye:
        kisiler = kisiler.filter(atolye_id=atolye)
    if pozisyon:
        kisiler = kisiler.filter(pozisyon_id=pozisyon)
    return render(
        request,
        "panel/kisi_listesi.html",
        {
            "kisiler": kisiler,
            "atolyeler": Atolye.objects.all(),
            "pozisyonlar": Pozisyon.objects.all(),
            "secili_atolye": atolye,
            "secili_gorev": pozisyon,
        },
    )


def _form_kaydet(request, form, basari, hedef, baslik):
    if request.method == "POST" and form.is_valid():
        nesne = form.save()
        messages.success(request, basari.format(nesne))
        return redirect(hedef)
    return render(request, "form_sayfasi.html", {"form": form, "baslik": baslik, "geri": hedef, "panel": True})


@admin_gerekli
def kisi_ekle(request):
    ilk = {}
    if request.GET.get("gorev"):
        ilk["pozisyon"] = request.GET["gorev"]
    form = KisiEklemeFormu(request.POST or None, initial=ilk)
    return _form_kaydet(request, form, "{} eklendi.", "kisi_listesi", "Yeni kişi")


@admin_gerekli
def kisi_duzenle(request, pk):
    kisi = get_object_or_404(Kullanici, pk=pk)
    form = KisiFormu(request.POST or None, instance=kisi)
    if request.method == "POST" and form.is_valid() and kisi == request.user:
        if not form.cleaned_data["is_active"] or not form.cleaned_data["is_staff"] and not kisi.is_superuser:
            form.add_error(None, "Kendi admin yetkinizi veya hesabınızı kapatamazsınız.")
            return render(request, "form_sayfasi.html", {"form": form, "baslik": f"{kisi}", "geri": "kisi_listesi", "panel": True})
    return _form_kaydet(request, form, "{} güncellendi.", "kisi_listesi", f"{kisi} düzenle")


@admin_gerekli
def kisi_sifre(request, pk):
    kisi = get_object_or_404(Kullanici, pk=pk)
    form = SifreBelirlemeFormu(kisi, request.POST or None)
    return _form_kaydet(request, form, "Yeni şifre belirlendi.", "kisi_listesi", f"{kisi} için yeni şifre")


@admin_gerekli
def pozisyon_listesi(request):
    return render(request, "panel/pozisyon_listesi.html", {"pozisyonlar": Pozisyon.objects.annotate(sayi=Count("kisiler"))})


@admin_gerekli
def pozisyon_ekle(request):
    return _form_kaydet(request, PozisyonFormu(request.POST or None), "{} görevi eklendi.", "pozisyon_listesi", "Yeni görev")


@admin_gerekli
def pozisyon_duzenle(request, pk):
    p = get_object_or_404(Pozisyon, pk=pk)
    return _form_kaydet(request, PozisyonFormu(request.POST or None, instance=p), "{} güncellendi.", "pozisyon_listesi", f"{p} düzenle")


@admin_gerekli
def atolye_listesi(request):
    return render(request, "panel/atolye_listesi.html", {"atolyeler": Atolye.objects.annotate(sayi=Count("kisiler"))})


@admin_gerekli
def atolye_ekle(request):
    return _form_kaydet(request, AtolyeFormu(request.POST or None), "{} eklendi.", "atolye_listesi", "Yeni atölye")


@admin_gerekli
def atolye_duzenle(request, pk):
    a = get_object_or_404(Atolye, pk=pk)
    return _form_kaydet(request, AtolyeFormu(request.POST or None, instance=a), "{} güncellendi.", "atolye_listesi", f"{a} düzenle")

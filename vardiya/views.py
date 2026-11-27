import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from hesaplar.models import Atolye

from .forms import ArizaFormu
from .models import ArizaKaydi, Durum, Vardiya, simdiki_vardiya


def _gorunur_kayitlar(kullanici):
    qs = ArizaKaydi.objects.select_related("atolye", "postabasi", "olusturan", "kapatan")
    if not kullanici.tum_atolyeleri_gorur:
        qs = qs.filter(atolye_id=kullanici.atolye_id)
    return qs


@login_required
def defter(request):
    kayitlar = _gorunur_kayitlar(request.user)
    bugun = timezone.localdate()
    try:
        tarih = datetime.date.fromisoformat(request.GET.get("tarih", ""))
    except ValueError:
        tarih = bugun
    atolye = request.GET.get("atolye", "")
    if atolye:
        kayitlar = kayitlar.filter(atolye_id=atolye)

    acik = kayitlar.filter(durum=Durum.DEVAM).order_by("tarih", "vardiya", "olusturma")
    gunun = kayitlar.filter(tarih=tarih)
    vardiyalar = [(v, [k for k in gunun if k.vardiya == v.value]) for v in reversed(Vardiya)]

    return render(
        request,
        "vardiya/defter.html",
        {
            "acik": acik,
            "vardiyalar": vardiyalar,
            "tarih": tarih,
            "bugun": bugun,
            "onceki": tarih - datetime.timedelta(days=1),
            "sonraki": tarih + datetime.timedelta(days=1),
            "simdiki": simdiki_vardiya(),
            "atolyeler": Atolye.objects.filter(aktif=True) if request.user.tum_atolyeleri_gorur else None,
            "secili_atolye": atolye,
        },
    )


@login_required
def kayit_ekle(request):
    form = ArizaFormu(request.POST or None, kullanici=request.user)
    if request.method == "POST" and form.is_valid():
        kayit = form.save(commit=False)
        kayit.olusturan = request.user
        if kayit.durum == Durum.BITTI:
            kayit.kapatan, kayit.kapanma = request.user, timezone.now()
        kayit.save()
        messages.success(request, "Arıza kaydı eklendi.")
        return redirect("defter")
    return render(request, "vardiya/kayit_formu.html", {"form": form, "baslik": "Yeni arıza kaydı"})


@login_required
def kayit_duzenle(request, pk):
    kayit = get_object_or_404(ArizaKaydi, pk=pk)
    if not kayit.kullanici_duzenleyebilir(request.user):
        raise PermissionDenied
    eski_durum = kayit.durum
    form = ArizaFormu(request.POST or None, instance=kayit, kullanici=request.user)
    if request.method == "POST" and form.is_valid():
        kayit = form.save(commit=False)
        if eski_durum == Durum.DEVAM and kayit.durum == Durum.BITTI:
            kayit.kapatan, kayit.kapanma = request.user, timezone.now()
        elif kayit.durum == Durum.DEVAM:
            kayit.kapatan, kayit.kapanma = None, None
        kayit.save()
        messages.success(request, "Kayıt güncellendi.")
        return redirect("defter")
    return render(request, "vardiya/kayit_formu.html", {"form": form, "baslik": "Kaydı düzenle", "kayit": kayit})


@login_required
def kayit_kapat(request, pk):
    """Devreden bir işi tek adımda kapatır: sadece yapılan işi yazıp 'Tamamlandı' der."""
    kayit = get_object_or_404(ArizaKaydi, pk=pk, durum=Durum.DEVAM)
    if not kayit.kullanici_duzenleyebilir(request.user):
        raise PermissionDenied
    if request.method == "POST":
        ek = request.POST.get("yapilan_is", "").strip()
        if not ek:
            messages.error(request, "Kapatmak için yapılan işi yazın.")
            return redirect("defter")
        zaman = timezone.localtime().strftime("%d.%m %H:%M")
        kayit.yapilan_is = (kayit.yapilan_is + "\n" if kayit.yapilan_is else "") + f"[{zaman} {request.user}] {ek}"
        kayit.durum = Durum.BITTI
        kayit.kapatan, kayit.kapanma = request.user, timezone.now()
        kayit.save()
        messages.success(request, f"{kayit.ekipman} işi tamamlandı olarak kapatıldı.")
    return redirect("defter")

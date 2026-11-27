from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from hesaplar.models import Atolye, Kullanici

from . import servis
from .forms import IsFormu
from .models import ACIK_DURUMLAR, Bildirim, Durum, Is

SEKMELER = [("bana", "Bana atananlar"), ("acik", "Açık işler"), ("onay", "Onay bekleyenler"), ("biten", "Bitenler")]


@login_required
def liste(request):
    k = request.user
    isler = servis.gorunur_isler(k)
    varsayilan = "bana" if k.personel_mi else "acik"
    sekme = request.GET.get("sekme", varsayilan)
    if sekme == "bana":
        isler = isler.filter(sorumlu=k, durum__in=ACIK_DURUMLAR)
    elif sekme == "onay":
        isler = isler.filter(durum=Durum.TAMAMLANDI)
    elif sekme == "biten":
        isler = isler.filter(durum=Durum.ONAYLANDI).order_by("-tamamlanma")[:100]
    else:
        sekme = "acik"
        isler = isler.filter(durum__in=ACIK_DURUMLAR)
    atolye = request.GET.get("atolye", "")
    if atolye and sekme != "biten":
        isler = isler.filter(atolye_id=atolye)
    acik = servis.gorunur_isler(k).filter(durum__in=ACIK_DURUMLAR)
    sayilar = {
        "bana": acik.filter(sorumlu=k).count(),
        "acik": acik.count(),
        "onay": servis.gorunur_isler(k).filter(durum=Durum.TAMAMLANDI).count(),
    }
    return render(request, "isler/liste.html", {
        "isler": isler, "sekme": sekme, "sekmeler": SEKMELER, "sayilar": sayilar,
        "atolyeler": Atolye.objects.filter(aktif=True) if k.tum_atolyeleri_gorur else None,
        "secili_atolye": atolye, "simdi": timezone.now(),
    })


@login_required
def yeni(request):
    if not request.user.is_istegi_olusturabilir:
        raise PermissionDenied
    form = IsFormu(request.POST or None, kullanici=request.user)
    if request.method == "POST" and form.is_valid():
        is_ = form.save(commit=False)
        servis.kaydet_yeni(is_, request.user)
        messages.success(request, "İş oluşturuldu" + (f" ve {is_.sorumlu} kişisine atandı." if is_.sorumlu else ", atölye formenine bildirildi."))
        return redirect(is_)
    return render(request, "isler/form.html", {"form": form, "baslik": "Yeni iş isteği"})


@login_required
def duzenle(request, pk):
    is_ = get_object_or_404(Is, pk=pk)
    if not is_.yonetebilir(request.user):
        raise PermissionDenied
    eski_sorumlu, eski_son = is_.sorumlu_id, is_.son_tarih
    form = IsFormu(request.POST or None, instance=is_, kullanici=request.user)
    if request.method == "POST" and form.is_valid():
        is_ = form.save(commit=False)
        if is_.son_tarih != eski_son:
            is_.gecikme_bildirildi = False
        is_.save()
        if is_.sorumlu_id and is_.sorumlu_id != eski_sorumlu:
            servis.ata(is_, is_.sorumlu, request.user)
        messages.success(request, "İş güncellendi.")
        return redirect(is_)
    return render(request, "isler/form.html", {"form": form, "baslik": "İşi düzenle", "gorev": is_})


@login_required
def detay(request, pk):
    is_ = get_object_or_404(Is.objects.select_related("atolye", "sorumlu", "olusturan"), pk=pk)
    k = request.user
    if not is_.gorebilir(k):
        raise PermissionDenied
    Bildirim.objects.filter(alici=k, gorev=is_, okundu=False).update(okundu=True)
    return render(request, "isler/detay.html", {
        "gorev": is_,
        "hareketler": is_.hareketler.select_related("kisi"),
        "yonetebilir": is_.yonetebilir(k),
        "onaylayabilir": is_.onaylayabilir(k),
        "calisabilir": is_.calisabilir(k),
        "kisiler": is_.atanabilir_kisiler() if is_.yonetebilir(k) else None,
        "Durum": Durum,
    })


@login_required
@require_POST
def islem(request, pk):
    """Detay sayfasındaki tüm düğmeler buraya gelir."""
    is_ = get_object_or_404(Is, pk=pk)
    k, eylem, notu = request.user, request.POST.get("eylem"), request.POST.get("notu", "").strip()

    if eylem == "ata" and is_.yonetebilir(k) and is_.acik_mi:
        sorumlu = get_object_or_404(is_.atanabilir_kisiler(), pk=request.POST.get("sorumlu"))
        servis.ata(is_, sorumlu, k)
        messages.success(request, f"{sorumlu} kişisine atandı.")
    elif eylem == "basla" and is_.calisabilir(k) and is_.durum == Durum.ATANDI:
        servis.basla(is_, k)
    elif eylem == "bitir" and is_.calisabilir(k) and is_.durum in (Durum.ATANDI, Durum.DEVAM):
        servis.bitir(is_, k, notu)
        messages.success(request, "İş tamamlandı, onaya gönderildi.")
    elif eylem == "onayla" and is_.onaylayabilir(k) and is_.durum == Durum.TAMAMLANDI:
        servis.onayla(is_, k)
        messages.success(request, "İş onaylandı ve kapandı.")
    elif eylem == "geri" and is_.onaylayabilir(k) and is_.durum == Durum.TAMAMLANDI:
        servis.geri_gonder(is_, k, notu)
        messages.success(request, "İş geri gönderildi.")
    elif eylem == "yorum" and is_.gorebilir(k) and notu:
        servis.yorum(is_, k, notu)
    else:
        raise PermissionDenied
    return redirect(is_)


@login_required
def bildirimler(request):
    liste = request.user.bildirimler.select_related("gorev")[:50]
    yanit = render(request, "isler/bildirimler.html", {"bildirimler": list(liste)})
    request.user.bildirimler.filter(okundu=False).update(okundu=True)
    return yanit


@login_required
def bildirim_durumu(request):
    """Açık sayfalar bunu 15 saniyede bir sorar."""
    servis.gecikmeleri_bildir()
    okunmamis = request.user.bildirimler.filter(okundu=False)
    son = okunmamis.first()
    return JsonResponse({
        "sayi": okunmamis.count(),
        "son_id": son.pk if son else 0,
        "son_metin": son.metin if son else "",
        "son_url": son.gorev.get_absolute_url() if son else "",
    })

"""İş akışı: durum değişiklikleri, geçmiş kaydı ve bildirimler tek yerden."""
from django.db.models import Q
from django.utils import timezone

from hesaplar.models import Kullanici, Yetki

from .models import ACIK_DURUMLAR, Bildirim, Durum, Hareket, Is


def _bildir(is_, kisiler, metin, haric=None):
    gorulen = set()
    for k in kisiler:
        if k and k.is_active and k.pk not in gorulen and (haric is None or k.pk != haric.pk):
            gorulen.add(k.pk)
            Bildirim.objects.create(alici=k, gorev=is_, metin=metin)


def _formenler(is_):
    return Kullanici.objects.filter(is_active=True, atolye_id=is_.atolye_id, pozisyon__yetki=Yetki.FORMEN)


def kaydet_yeni(is_, kisi):
    is_.olusturan = kisi
    is_.durum = Durum.ATANDI if is_.sorumlu_id else Durum.ATANMADI
    is_.save()
    Hareket.objects.create(gorev=is_, kisi=kisi, metin="İşi oluşturdu.")
    _bildir(is_, _formenler(is_), f"Yeni iş: {is_.baslik} ({is_.atolye})", haric=kisi)
    if is_.sorumlu_id:
        Hareket.objects.create(gorev=is_, kisi=kisi, metin=f"{is_.sorumlu} kişisine atadı.")
        _bildir(is_, [is_.sorumlu], f"Size iş atandı: {is_.baslik}", haric=kisi)


def ata(is_, sorumlu, kisi):
    is_.sorumlu = sorumlu
    if is_.durum in (Durum.ATANMADI, Durum.ATANDI):
        is_.durum = Durum.ATANDI
    is_.save()
    Hareket.objects.create(gorev=is_, kisi=kisi, metin=f"{sorumlu} kişisine atadı.")
    _bildir(is_, [sorumlu], f"Size iş atandı: {is_.baslik}", haric=kisi)


def basla(is_, kisi):
    is_.durum = Durum.DEVAM
    is_.save()
    Hareket.objects.create(gorev=is_, kisi=kisi, metin="İşe başladı.")


def bitir(is_, kisi, notu):
    is_.durum = Durum.TAMAMLANDI
    is_.tamamlanma = timezone.now()
    is_.save()
    Hareket.objects.create(gorev=is_, kisi=kisi, metin="İşi tamamladı." + (f" {notu}" if notu else ""))
    _bildir(is_, [is_.olusturan, *_formenler(is_)], f"İş tamamlandı, onay bekliyor: {is_.baslik}", haric=kisi)


def onayla(is_, kisi):
    is_.durum = Durum.ONAYLANDI
    is_.save()
    Hareket.objects.create(gorev=is_, kisi=kisi, metin="Onayladı ve işi kapattı.")
    _bildir(is_, [is_.sorumlu], f"İşiniz onaylandı: {is_.baslik}", haric=kisi)


def geri_gonder(is_, kisi, notu):
    is_.durum = Durum.DEVAM
    is_.tamamlanma = None
    is_.save()
    Hareket.objects.create(gorev=is_, kisi=kisi, metin="Geri gönderdi." + (f" {notu}" if notu else ""))
    _bildir(is_, [is_.sorumlu], f"İş geri gönderildi: {is_.baslik}", haric=kisi)


def yorum(is_, kisi, metin):
    Hareket.objects.create(gorev=is_, kisi=kisi, metin=metin)
    _bildir(is_, [is_.sorumlu, is_.olusturan], f"{kisi} not yazdı: {is_.baslik}", haric=kisi)


def gecikmeleri_bildir():
    """Süresi dolan açık işler için bir kez bildirim üretir. Ayrı bir zamanlayıcıya gerek kalmasın diye
    her bildirim kontrolünde (sayfalar 15 sn'de bir sorar) çağrılır."""
    for is_ in Is.objects.filter(durum__in=ACIK_DURUMLAR, son_tarih__lt=timezone.now(), gecikme_bildirildi=False):
        is_.gecikme_bildirildi = True
        is_.save(update_fields=["gecikme_bildirildi"])
        Hareket.objects.create(gorev=is_, kisi=None, metin="Süre doldu.")
        _bildir(is_, [is_.sorumlu, is_.olusturan, *_formenler(is_)], f"Süresi doldu: {is_.baslik}")


def gorunur_isler(k):
    qs = Is.objects.select_related("atolye", "sorumlu", "olusturan")
    if k.tum_atolyeleri_gorur:
        return qs
    return qs.filter(Q(atolye_id=k.atolye_id) | Q(sorumlu=k) | Q(olusturan=k))

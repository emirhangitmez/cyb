from django.conf import settings
from django.db import models
from django.utils import timezone

from hesaplar.models import Atolye


class Vardiya(models.IntegerChoices):
    GECE = 1, "00:00 - 08:00"
    SABAH = 2, "08:00 - 16:00"
    AKSAM = 3, "16:00 - 24:00"


def simdiki_vardiya(an=None):
    """Verilen andaki (varsayılan: şimdi) vardiyayı döndürür."""
    an = timezone.localtime(an)
    if an.hour < 8:
        return Vardiya.GECE
    if an.hour < 16:
        return Vardiya.SABAH
    return Vardiya.AKSAM


class Durum(models.TextChoices):
    DEVAM = "DEVAM", "Devam ediyor (sonraki vardiyaya devredildi)"
    BITTI = "BITTI", "Tamamlandı"


class ArizaKaydi(models.Model):
    tarih = models.DateField("Tarih", default=timezone.localdate)
    vardiya = models.PositiveSmallIntegerField("Vardiya", choices=Vardiya.choices, default=simdiki_vardiya)
    atolye = models.ForeignKey(Atolye, verbose_name="Atölye", on_delete=models.PROTECT, related_name="ariza_kayitlari")
    postabasi = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Postabaşı", on_delete=models.PROTECT, related_name="postabasi_kayitlari"
    )
    ekipman = models.CharField("Makine / Hat / Ekipman", max_length=150)
    ariza = models.TextField("Arıza")
    yapilan_is = models.TextField("Yapılan iş", blank=True)
    durum = models.CharField("Durum", max_length=10, choices=Durum.choices, default=Durum.BITTI)
    notlar = models.TextField("Not", blank=True)

    olusturan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="olusturdugu_kayitlar", editable=False
    )
    olusturma = models.DateTimeField(auto_now_add=True)
    guncelleme = models.DateTimeField(auto_now=True)
    kapatan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="kapattigi_kayitlar", editable=False
    )
    kapanma = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "Arıza kaydı"
        verbose_name_plural = "Arıza kayıtları"
        ordering = ["-tarih", "-vardiya", "-olusturma"]

    def __str__(self):
        return f"{self.tarih:%d.%m.%Y} {self.get_vardiya_display()} · {self.ekipman}"

    @property
    def acik_mi(self):
        return self.durum == Durum.DEVAM

    def kullanici_duzenleyebilir(self, kullanici):
        return kullanici.tum_atolyeleri_gorur or kullanici.atolye_id == self.atolye_id

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from hesaplar.models import Atolye, Kullanici, Yetki


class Durum(models.TextChoices):
    ATANMADI = "ATANMADI", "Kişi atanmadı"
    ATANDI = "ATANDI", "Atandı"
    DEVAM = "DEVAM", "Devam ediyor"
    TAMAMLANDI = "TAMAMLANDI", "Tamamlandı (onay bekliyor)"
    ONAYLANDI = "ONAYLANDI", "Onaylandı"


ACIK_DURUMLAR = [Durum.ATANMADI, Durum.ATANDI, Durum.DEVAM]


class Oncelik(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    ACIL = "ACIL", "Acil"


class Is(models.Model):
    baslik = models.CharField("Ne yapılacak?", max_length=150)
    aciklama = models.TextField("Açıklama", blank=True)
    atolye = models.ForeignKey(Atolye, verbose_name="Atölye", on_delete=models.PROTECT, related_name="isler")
    ekipman = models.CharField("Makine / Hat", max_length=150, blank=True)
    oncelik = models.CharField("Öncelik", max_length=10, choices=Oncelik.choices, default=Oncelik.NORMAL)
    son_tarih = models.DateTimeField("Bitiş süresi")
    sorumlu = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Atanan kişi", on_delete=models.PROTECT,
        null=True, blank=True, related_name="atanan_isler",
    )
    durum = models.CharField("Durum", max_length=12, choices=Durum.choices, default=Durum.ATANMADI)

    olusturan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="olusturdugu_isler")
    olusturma = models.DateTimeField(auto_now_add=True)
    tamamlanma = models.DateTimeField(null=True, blank=True)
    gecikme_bildirildi = models.BooleanField(default=False)

    class Meta:
        verbose_name = "İş"
        verbose_name_plural = "İşler"
        ordering = ["son_tarih"]

    def __str__(self):
        return self.baslik

    def get_absolute_url(self):
        return reverse("is_detay", args=[self.pk])

    @property
    def acik_mi(self):
        return self.durum in ACIK_DURUMLAR

    @property
    def gecikti_mi(self):
        return self.acik_mi and self.son_tarih < timezone.now()

    # --- Kim ne yapabilir ---
    def yonetebilir(self, k):
        """Kişi atama ve düzenleme: müdür her işte; mühendis ve formen sadece kendi atölyesinin işlerinde."""
        if not k.gorev_atayabilir:
            return False
        return k.tum_atolyeleri_gorur or k.atolye_id == self.atolye_id

    def onaylayabilir(self, k):
        """Onay atölyenin mühendisinindir. Müdürün de onay hakkı vardır ama beklenmez. Formen onaylamaz."""
        if k.mudur_mu:
            return True
        return k.muhendis_mi and (not k.atolye_id or k.atolye_id == self.atolye_id)

    def calisabilir(self, k):
        """Başladım / Bitirdim: atanan kişi veya yönetebilenler."""
        return k.pk == self.sorumlu_id or self.yonetebilir(k)

    def gorebilir(self, k):
        return (
            k.tum_atolyeleri_gorur or k.atolye_id == self.atolye_id
            or k.pk in (self.sorumlu_id, self.olusturan_id)
        )

    def atanabilir_kisiler(self):
        return Kullanici.objects.filter(
            is_active=True, atolye_id=self.atolye_id, pozisyon__yetki__in=[Yetki.PERSONEL, Yetki.FORMEN]
        ).order_by("first_name")


class Hareket(models.Model):
    """İşin geçmişi: kim, ne zaman, ne yaptı / ne yazdı."""

    gorev = models.ForeignKey(Is, on_delete=models.CASCADE, related_name="hareketler")
    kisi = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    zaman = models.DateTimeField(auto_now_add=True)
    metin = models.TextField()

    class Meta:
        ordering = ["zaman"]


class Bildirim(models.Model):
    alici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bildirimler")
    gorev = models.ForeignKey(Is, on_delete=models.CASCADE, related_name="bildirimler")
    metin = models.CharField(max_length=250)
    zaman = models.DateTimeField(auto_now_add=True)
    okundu = models.BooleanField(default=False)

    class Meta:
        ordering = ["-zaman"]

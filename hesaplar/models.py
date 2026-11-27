from django.contrib.auth.models import AbstractUser
from django.db import models


class Yetki(models.TextChoices):
    """Uygulamanın tanıdığı yetki seviyeleri. Görev (pozisyon) isimleri admin tarafından serbestçe
    girilir, her görev bu seviyelerden birine bağlanır."""

    MUDUR = "MUDUR", "Müdür yetkisi"
    MUHENDIS = "MUHENDIS", "Mühendis yetkisi"
    FORMEN = "FORMEN", "Formen yetkisi"
    PERSONEL = "PERSONEL", "Personel yetkisi"


# Eski isimle uyumluluk
Rol = Yetki


class Atolye(models.Model):
    ad = models.CharField("Atölye adı", max_length=80, unique=True)
    kod = models.CharField("Kısa kod", max_length=20, unique=True, help_text="Ör. ELK, MEK")
    aciklama = models.CharField("Açıklama", max_length=200, blank=True)
    aktif = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "Atölye"
        verbose_name_plural = "Atölyeler"
        ordering = ["ad"]

    def __str__(self):
        return self.ad


class Pozisyon(models.Model):
    """Kişiye verilen görev/unvan: Müdür, Mühendis, Formen, Personel, Postabaşı vb."""

    ad = models.CharField("Görev adı", max_length=80, unique=True)
    yetki = models.CharField("Yetki seviyesi", max_length=20, choices=Yetki.choices, default=Yetki.PERSONEL)
    atolye_gerekli = models.BooleanField(
        "Atölye seçimi zorunlu", default=True, help_text="Müdür/mühendis gibi tüm atölyeleri görenler için kaldırın."
    )
    sira = models.PositiveSmallIntegerField("Sıra", default=10, help_text="Listelerde küçük olan önce gelir.")
    aktif = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "Görev"
        verbose_name_plural = "Görevler"
        ordering = ["sira", "ad"]

    def __str__(self):
        return self.ad


class Kullanici(AbstractUser):
    pozisyon = models.ForeignKey(
        Pozisyon, verbose_name="Görev", on_delete=models.PROTECT, null=True, blank=True, related_name="kisiler"
    )
    atolye = models.ForeignKey(
        Atolye, verbose_name="Atölye", on_delete=models.PROTECT, null=True, blank=True, related_name="kisiler"
    )
    sicil_no = models.CharField("Sicil No", max_length=30, blank=True)
    telefon = models.CharField("Telefon", max_length=30, blank=True)

    class Meta:
        verbose_name = "Kişi"
        verbose_name_plural = "Kişiler"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.get_full_name() or self.username

    # --- Yetki yardımcıları ---
    @property
    def rol(self):
        return self.pozisyon.yetki if self.pozisyon_id else None

    @property
    def admin_mi(self):
        return self.is_superuser or self.is_staff

    @property
    def mudur_mu(self):
        return self.rol == Yetki.MUDUR

    @property
    def muhendis_mi(self):
        return self.rol == Yetki.MUHENDIS

    @property
    def formen_mi(self):
        return self.rol == Yetki.FORMEN

    @property
    def personel_mi(self):
        return self.rol == Yetki.PERSONEL

    @property
    def is_istegi_olusturabilir(self):
        """İş isteğini müdür, mühendis ve formen oluşturabilir."""
        return self.rol in (Yetki.MUDUR, Yetki.MUHENDIS, Yetki.FORMEN)

    @property
    def gorev_atayabilir(self):
        """Müdür, mühendis ve formen bir işe personel atayabilir."""
        return self.rol in (Yetki.MUDUR, Yetki.MUHENDIS, Yetki.FORMEN)

    @property
    def tum_atolyeleri_gorur(self):
        """Müdür ve admin tüm atölyeleri görür. Mühendis, formen ve personel kendi atölyesiyle sınırlıdır
        (ör. elektrik bakım mühendisi sadece elektrik atölyesi)."""
        return self.admin_mi or self.rol == Yetki.MUDUR or not self.atolye_id

from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    MUDUR = "MUDUR", "Müdür"
    MUHENDIS = "MUHENDIS", "Mühendis"
    FORMEN = "FORMEN", "Formen"
    PERSONEL = "PERSONEL", "Personel"


class Atolye(models.TextChoices):
    ELEKTRIK = "ELEKTRIK", "Elektrik Atölyesi"
    MEKANIK = "MEKANIK", "Mekanik Atölyesi"


class Kullanici(AbstractUser):
    """Uygulamaya giriş yapan kişi. Her kullanıcının bir rolü ve (müdür hariç) bir atölyesi vardır."""

    rol = models.CharField("Rol", max_length=20, choices=Rol.choices, default=Rol.PERSONEL)
    atolye = models.CharField(
        "Atölye",
        max_length=20,
        choices=Atolye.choices,
        blank=True,
        help_text="Müdür için boş bırakılabilir (tüm atölyeleri görür).",
    )
    sicil_no = models.CharField("Sicil No", max_length=30, blank=True)
    telefon = models.CharField("Telefon", max_length=30, blank=True)

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        ordering = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        # Komut satırından oluşturulan ilk yönetici hesabı müdür olsun
        if self.is_superuser and not self.pk:
            self.rol = Rol.MUDUR
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username

    # --- Yetki yardımcıları ---
    @property
    def mudur_mu(self):
        return self.rol == Rol.MUDUR

    @property
    def muhendis_mi(self):
        return self.rol == Rol.MUHENDIS

    @property
    def formen_mi(self):
        return self.rol == Rol.FORMEN

    @property
    def personel_mi(self):
        return self.rol == Rol.PERSONEL

    @property
    def kullanici_yonetebilir(self):
        return self.mudur_mu

    @property
    def is_istegi_olusturabilir(self):
        """İş isteğini müdür, mühendis ve formen oluşturabilir."""
        return self.rol in (Rol.MUDUR, Rol.MUHENDIS, Rol.FORMEN)

    @property
    def gorev_atayabilir(self):
        """Formen kendi atölyesindeki personele görev atar; müdür de atayabilir."""
        return self.rol in (Rol.MUDUR, Rol.FORMEN)

    @property
    def tum_atolyeleri_gorur(self):
        return self.rol in (Rol.MUDUR, Rol.MUHENDIS) or not self.atolye

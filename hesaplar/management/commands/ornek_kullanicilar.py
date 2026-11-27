from django.core.management.base import BaseCommand

from hesaplar.models import Atolye, Kullanici, Rol

ORNEKLER = [
    ("mudur", "Bakım", "Müdürü", Rol.MUDUR, ""),
    ("muhendis", "Bakım", "Mühendisi", Rol.MUHENDIS, ""),
    ("elektrik.formen", "Elektrik", "Formeni", Rol.FORMEN, Atolye.ELEKTRIK),
    ("mekanik.formen", "Mekanik", "Formeni", Rol.FORMEN, Atolye.MEKANIK),
    ("elektrik.personel", "Elektrik", "Teknisyeni", Rol.PERSONEL, Atolye.ELEKTRIK),
    ("mekanik.personel", "Mekanik", "Teknisyeni", Rol.PERSONEL, Atolye.MEKANIK),
]


class Command(BaseCommand):
    help = "Deneme için her rolden örnek kullanıcı oluşturur (şifre: 123456). Gerçek kullanımda silin."

    def handle(self, *args, **kwargs):
        for kadi, ad, soyad, rol, atolye in ORNEKLER:
            k, yeni = Kullanici.objects.get_or_create(
                username=kadi, defaults={"first_name": ad, "last_name": soyad, "rol": rol, "atolye": atolye}
            )
            if yeni:
                k.set_password("123456")
                k.save()
            self.stdout.write(f"{'Oluşturuldu' if yeni else 'Zaten var'}: {kadi}")

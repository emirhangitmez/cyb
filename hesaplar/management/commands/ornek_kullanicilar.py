from django.core.management.base import BaseCommand

from hesaplar.models import Atolye, Kullanici, Pozisyon

ORNEKLER = [
    # kullanıcı adı, ad, soyad, görev, atölye kodu
    ("mudur", "Bakım", "Müdürü", "Müdür", None),
    ("muhendis", "Bakım", "Mühendisi", "Mühendis", None),
    ("elektrik.formen", "Elektrik", "Formeni", "Formen", "ELK"),
    ("mekanik.formen", "Mekanik", "Formeni", "Formen", "MEK"),
    ("elektrik.personel", "Elektrik", "Teknisyeni", "Personel", "ELK"),
    ("mekanik.personel", "Mekanik", "Teknisyeni", "Personel", "MEK"),
]


class Command(BaseCommand):
    help = "Deneme için admin ve her görevden örnek kişi oluşturur (şifre: 123456). Gerçek kullanımda kullanmayın."

    def handle(self, *args, **kwargs):
        admin, yeni = Kullanici.objects.get_or_create(
            username="admin", defaults={"first_name": "Sistem", "last_name": "Yöneticisi", "is_staff": True, "is_superuser": True}
        )
        if yeni:
            admin.set_password("123456")
            admin.save()
        for kadi, ad, soyad, gorev, atolye in ORNEKLER:
            k, yeni = Kullanici.objects.get_or_create(
                username=kadi,
                defaults={
                    "first_name": ad,
                    "last_name": soyad,
                    "pozisyon": Pozisyon.objects.get(ad=gorev),
                    "atolye": Atolye.objects.get(kod=atolye) if atolye else None,
                },
            )
            if yeni:
                k.set_password("123456")
                k.save()
            self.stdout.write(f"{'Oluşturuldu' if yeni else 'Zaten var'}: {kadi}")

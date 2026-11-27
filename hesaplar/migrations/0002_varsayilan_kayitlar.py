from django.db import migrations

ATOLYELER = [("Elektrik Atölyesi", "ELK"), ("Mekanik Atölyesi", "MEK")]
GOREVLER = [
    # ad, yetki, atölye zorunlu mu, sıra
    ("Müdür", "MUDUR", False, 1),
    ("Mühendis", "MUHENDIS", False, 2),
    ("Formen", "FORMEN", True, 3),
    ("Personel", "PERSONEL", True, 4),
]


def ekle(apps, schema_editor):
    Atolye = apps.get_model("hesaplar", "Atolye")
    Pozisyon = apps.get_model("hesaplar", "Pozisyon")
    for ad, kod in ATOLYELER:
        Atolye.objects.get_or_create(kod=kod, defaults={"ad": ad})
    for ad, yetki, gerekli, sira in GOREVLER:
        Pozisyon.objects.get_or_create(ad=ad, defaults={"yetki": yetki, "atolye_gerekli": gerekli, "sira": sira})


class Migration(migrations.Migration):
    dependencies = [("hesaplar", "0001_initial")]
    operations = [migrations.RunPython(ekle, migrations.RunPython.noop)]

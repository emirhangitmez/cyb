from django.db import migrations


def guncelle(apps, schema_editor):
    # Mühendisler artık bir atölyeye bağlı (elektrik bakım mühendisi / mekanik bakım mühendisi)
    apps.get_model("hesaplar", "Pozisyon").objects.filter(yetki="MUHENDIS").update(atolye_gerekli=True)


class Migration(migrations.Migration):
    dependencies = [("hesaplar", "0002_varsayilan_kayitlar")]
    operations = [migrations.RunPython(guncelle, migrations.RunPython.noop)]

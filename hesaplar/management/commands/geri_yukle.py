import shutil
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Bir yedek dosyasını geri yükler. Önce sunucuyu durdurun. Mevcut veritabanı da ayrıca yedeklenir."

    def add_arguments(self, parser):
        parser.add_argument("yedek", nargs="?", help="Yedek dosyası. Boş bırakılırsa en yeni yedek kullanılır.")
        parser.add_argument("--evet", action="store_true", help="Onay sormadan yükle.")

    def handle(self, *args, yedek=None, evet=False, **kwargs):
        klasor = Path(settings.YEDEK_KLASORU)
        if yedek:
            kaynak = Path(yedek)
        else:
            yedekler = sorted(klasor.glob("vardiya-*.sqlite3"))
            if not yedekler:
                raise CommandError(f"{klasor} içinde yedek bulunamadı.")
            kaynak = yedekler[-1]
        if not kaynak.exists():
            raise CommandError(f"Dosya bulunamadı: {kaynak}")
        with sqlite3.connect(kaynak) as k:
            if k.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise CommandError("Yedek dosyası bozuk görünüyor, yüklenmedi.")

        db = Path(settings.DATABASES["default"]["NAME"])
        if not evet and input(f"{kaynak.name} geri yüklenecek, mevcut veriler bununla değişecek. Devam? (e/h) ").lower() != "e":
            self.stdout.write("Vazgeçildi.")
            return
        if db.exists():
            onceki = klasor / "geri-yukleme-oncesi.sqlite3"
            klasor.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(db) as eski, sqlite3.connect(onceki) as hedef:
                eski.backup(hedef)
            self.stdout.write(f"Mevcut veritabanı şuraya kaydedildi: {onceki}")
        for ek in ("-wal", "-shm"):
            Path(str(db) + ek).unlink(missing_ok=True)
        shutil.copyfile(kaynak, db)
        self.stdout.write(self.style.SUCCESS(f"Geri yüklendi: {kaynak.name}"))

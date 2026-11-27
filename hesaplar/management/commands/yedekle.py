import sqlite3
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone


class Command(BaseCommand):
    help = "Veritabanının tutarlı bir kopyasını yedek klasörüne alır ve eski yedekleri siler."

    def handle(self, *args, **kwargs):
        klasor = Path(settings.YEDEK_KLASORU)
        klasor.mkdir(parents=True, exist_ok=True)
        hedef = klasor / f"vardiya-{timezone.localtime():%Y-%m-%d_%H%M}.sqlite3"

        connection.ensure_connection()
        # SQLite'ın kendi yedek API'si: uygulama çalışırken bile güvenli kopya alır
        with sqlite3.connect(hedef) as yedek:
            connection.connection.backup(yedek)
        self.stdout.write(f"Yedek alındı: {hedef}")

        sinir = time.time() - settings.YEDEK_GUN * 86400
        for eski in klasor.glob("vardiya-*.sqlite3"):
            if eski.stat().st_mtime < sinir:
                eski.unlink()
                self.stdout.write(f"Eski yedek silindi: {eski.name}")

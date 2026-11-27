"""Vardiya Takip sunucusu.

Ağdaki diğer bilgisayarların tarayıcıdan bağlanacağı asıl sunucu budur (geliştirme sunucusu değil).
Çalıştırma:  venv\\Scripts\\python.exe sunucu.py
Port değiştirmek için: VARDIYA_PORT ortam değişkeni (varsayılan 8000).
"""
import os
import socket
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("VARDIYA_DEBUG", "0")

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402

django.setup()

from waitress import serve  # noqa: E402


def main():
    port = int(os.environ.get("VARDIYA_PORT", "8000"))
    call_command("migrate", interactive=False, verbosity=0)
    call_command("collectstatic", interactive=False, verbosity=0)
    # Uygulama, statik dosyalar toplandıktan sonra yüklenmeli
    from config.wsgi import application
    ad = socket.gethostname()
    print("=" * 60)
    print(" Vardiya Takip sunucusu çalışıyor")
    print(f" Bu bilgisayardan : http://localhost:{port}")
    print(f" Ağdaki diğerleri : http://{ad}:{port}")
    try:
        print(f"                    http://{socket.gethostbyname(ad)}:{port}")
    except OSError:
        pass
    print(" Kapatmak için bu pencereyi kapatın.")
    print("=" * 60)
    sys.stdout.flush()
    serve(application, host="0.0.0.0", port=port, threads=8)


if __name__ == "__main__":
    main()

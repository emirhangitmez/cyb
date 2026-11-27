from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from .models import Atolye, Kullanici, Pozisyon, Yetki


class TemelVeri(TestCase):
    def setUp(self):
        # 0002 göç dosyası varsayılan atölye ve görevleri ekler
        self.elk = Atolye.objects.get(kod="ELK")
        self.mek = Atolye.objects.get(kod="MEK")
        self.formen_g = Pozisyon.objects.get(ad="Formen")
        self.personel_g = Pozisyon.objects.get(ad="Personel")
        self.muhendis_g = Pozisyon.objects.get(ad="Mühendis")
        self.admin = Kullanici.objects.create_superuser("admin", password="sifre123")
        self.formen = Kullanici.objects.create_user("formen", password="sifre123", pozisyon=self.formen_g, atolye=self.elk)


class GirisTestleri(TemelVeri):
    def test_giris_yapmayan_yonlenir(self):
        self.assertRedirects(self.client.get(reverse("ana_sayfa")), reverse("giris") + "?next=/")

    def test_dogru_sifre_ile_giris(self):
        r = self.client.post(reverse("giris"), {"username": "formen", "password": "sifre123"})
        self.assertRedirects(r, reverse("ana_sayfa"))

    def test_yanlis_sifre_turkce_hata(self):
        r = self.client.post(reverse("giris"), {"username": "formen", "password": "yanlis"})
        self.assertContains(r, "Kullanıcı adı veya şifre hatalı.")

    def test_pasif_kisi_giris_yapamaz(self):
        self.formen.is_active = False
        self.formen.save()
        self.client.post(reverse("giris"), {"username": "formen", "password": "sifre123"})
        self.assertNotIn("_auth_user_id", self.client.session)


class AdminPaneliTestleri(TemelVeri):
    def test_varsayilan_kayitlar(self):
        self.assertEqual(Pozisyon.objects.count(), 4)
        self.assertEqual(Atolye.objects.count(), 2)

    def test_admin_olmayan_panele_giremez(self):
        self.client.force_login(self.formen)
        for ad in ["panel", "kisi_listesi", "pozisyon_listesi", "atolye_listesi", "kisi_ekle"]:
            self.assertEqual(self.client.get(reverse(ad)).status_code, 403, ad)

    def test_admin_tum_sayfalari_acar(self):
        self.client.force_login(self.admin)
        for ad in ["panel", "kisi_listesi", "pozisyon_listesi", "atolye_listesi", "kisi_ekle", "pozisyon_ekle", "atolye_ekle"]:
            self.assertEqual(self.client.get(reverse(ad)).status_code, 200, ad)

    def test_admin_kisi_ekler_ve_gorev_atar(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("kisi_ekle"), {
            "first_name": "Ali", "last_name": "Kaya", "username": "ali.kaya", "pozisyon": self.personel_g.pk,
            "atolye": self.mek.pk, "is_active": "on", "sifre1": "abc123", "sifre2": "abc123",
        })
        self.assertRedirects(r, reverse("kisi_listesi"))
        ali = Kullanici.objects.get(username="ali.kaya")
        self.assertTrue(ali.check_password("abc123"))
        self.assertEqual(ali.rol, Yetki.PERSONEL)
        self.assertEqual(ali.atolye, self.mek)

    def test_formen_icin_atolye_zorunlu(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("kisi_ekle"), {
            "first_name": "Veli", "username": "veli", "pozisyon": self.formen_g.pk, "atolye": "",
            "sifre1": "abc123", "sifre2": "abc123",
        })
        self.assertContains(r, "atölye seçilmelidir")

    def test_muhendis_atolyeye_baglidir(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("kisi_ekle"), {
            "first_name": "Ayşe", "username": "ayse", "pozisyon": self.muhendis_g.pk, "atolye": "",
            "is_active": "on", "sifre1": "abc123", "sifre2": "abc123",
        })
        self.assertContains(r, "atölye seçilmelidir")
        self.client.post(reverse("kisi_ekle"), {
            "first_name": "Ayşe", "username": "ayse", "pozisyon": self.muhendis_g.pk, "atolye": self.elk.pk,
            "is_active": "on", "sifre1": "abc123", "sifre2": "abc123",
        })
        self.assertFalse(Kullanici.objects.get(username="ayse").tum_atolyeleri_gorur)

    def test_yeni_gorev_ve_atolye_eklenir(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("pozisyon_ekle"), {"ad": "Postabaşı", "yetki": Yetki.FORMEN, "atolye_gerekli": "on", "sira": 5, "aktif": "on"})
        self.client.post(reverse("atolye_ekle"), {"ad": "Otomasyon Atölyesi", "kod": "OTO", "aktif": "on"})
        self.assertTrue(Pozisyon.objects.filter(ad="Postabaşı", yetki=Yetki.FORMEN).exists())
        self.assertTrue(Atolye.objects.filter(kod="OTO").exists())

    def test_admin_sifre_sifirlar(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("kisi_sifre", args=[self.formen.pk]), {"new_password1": "Yeni.Sifre9", "new_password2": "Yeni.Sifre9"})
        self.formen.refresh_from_db()
        self.assertTrue(self.formen.check_password("Yeni.Sifre9"))


class YetkiKurallari(TemelVeri):
    def test_yetkiler(self):
        personel = Kullanici(pozisyon=self.personel_g, atolye=self.elk)
        muhendis = Kullanici(pozisyon=self.muhendis_g)
        self.assertFalse(personel.is_istegi_olusturabilir)
        self.assertTrue(self.formen.is_istegi_olusturabilir)
        self.assertTrue(muhendis.is_istegi_olusturabilir)
        self.assertTrue(self.formen.gorev_atayabilir)
        self.assertTrue(muhendis.gorev_atayabilir)
        self.assertFalse(personel.gorev_atayabilir)


class YedekTestleri(TransactionTestCase):
    def test_yedek_alinir_ve_eskiler_silinir(self):
        import os
        import sqlite3
        import tempfile
        import time
        from pathlib import Path

        from django.core.management import call_command
        from django.test import override_settings

        with tempfile.TemporaryDirectory() as klasor, override_settings(YEDEK_KLASORU=klasor, YEDEK_GUN=30):
            eski = Path(klasor) / "vardiya-2020-01-01_0200.sqlite3"
            eski.write_bytes(b"")
            os.utime(eski, (time.time() - 40 * 86400,) * 2)
            call_command("yedekle", stdout=open(os.devnull, "w"))
            yedekler = list(Path(klasor).glob("vardiya-*.sqlite3"))
            self.assertEqual(len(yedekler), 1)
            self.assertNotEqual(yedekler[0], eski)
            with sqlite3.connect(yedekler[0]) as db:
                tablolar = {r[0] for r in db.execute("select name from sqlite_master where type='table'")}
            self.assertIn("hesaplar_kullanici", tablolar)

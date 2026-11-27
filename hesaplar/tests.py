from django.test import TestCase
from django.urls import reverse

from .models import Atolye, Kullanici, Rol


class GirisVeYetkiTestleri(TestCase):
    def setUp(self):
        self.mudur = Kullanici.objects.create_user("mudur", password="sifre123", rol=Rol.MUDUR)
        self.formen = Kullanici.objects.create_user(
            "formen", password="sifre123", rol=Rol.FORMEN, atolye=Atolye.ELEKTRIK
        )

    def test_giris_yapmayan_giris_sayfasina_yonlenir(self):
        r = self.client.get(reverse("ana_sayfa"))
        self.assertRedirects(r, reverse("giris") + "?next=/")

    def test_dogru_sifre_ile_giris(self):
        r = self.client.post(reverse("giris"), {"username": "formen", "password": "sifre123"})
        self.assertRedirects(r, reverse("ana_sayfa"))

    def test_yanlis_sifre_turkce_hata(self):
        r = self.client.post(reverse("giris"), {"username": "formen", "password": "yanlis"})
        self.assertContains(r, "Kullanıcı adı veya şifre hatalı.")

    def test_formen_kullanici_yonetimine_giremez(self):
        self.client.force_login(self.formen)
        self.assertEqual(self.client.get(reverse("kullanici_listesi")).status_code, 403)

    def test_mudur_kullanici_ekler(self):
        self.client.force_login(self.mudur)
        r = self.client.post(
            reverse("kullanici_ekle"),
            {
                "username": "ali", "first_name": "Ali", "last_name": "Kaya", "rol": Rol.PERSONEL,
                "atolye": Atolye.MEKANIK, "is_active": "on", "sifre1": "abc123", "sifre2": "abc123",
            },
        )
        self.assertRedirects(r, reverse("kullanici_listesi"))
        ali = Kullanici.objects.get(username="ali")
        self.assertTrue(ali.check_password("abc123"))
        self.assertEqual(ali.atolye, Atolye.MEKANIK)

    def test_personel_icin_atolye_zorunlu(self):
        self.client.force_login(self.mudur)
        r = self.client.post(
            reverse("kullanici_ekle"),
            {"username": "veli", "rol": Rol.PERSONEL, "atolye": "", "sifre1": "abc123", "sifre2": "abc123"},
        )
        self.assertContains(r, "atölye seçilmelidir")

    def test_pasif_kullanici_giris_yapamaz(self):
        self.formen.is_active = False
        self.formen.save()
        r = self.client.post(reverse("giris"), {"username": "formen", "password": "sifre123"})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_yetki_kurallari(self):
        personel = Kullanici(rol=Rol.PERSONEL, atolye=Atolye.ELEKTRIK)
        muhendis = Kullanici(rol=Rol.MUHENDIS)
        self.assertFalse(personel.is_istegi_olusturabilir)
        self.assertTrue(self.formen.is_istegi_olusturabilir)
        self.assertTrue(muhendis.is_istegi_olusturabilir)
        self.assertTrue(self.formen.gorev_atayabilir)
        self.assertFalse(muhendis.gorev_atayabilir)

    def test_superuser_mudur_olur(self):
        s = Kullanici.objects.create_superuser("admin", password="x")
        self.assertEqual(s.rol, Rol.MUDUR)

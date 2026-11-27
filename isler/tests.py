import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from hesaplar.models import Atolye, Kullanici, Pozisyon

from .models import Bildirim, Durum, Is


def zaman(saat):
    return (timezone.localtime() + datetime.timedelta(hours=saat)).strftime("%Y-%m-%dT%H:%M")


class IsAkisi(TestCase):
    def setUp(self):
        self.elk = Atolye.objects.get(kod="ELK")
        self.mek = Atolye.objects.get(kod="MEK")
        P = lambda ad: Pozisyon.objects.get(ad=ad)  # noqa: E731
        self.mudur = Kullanici.objects.create_user("mudur", password="x", pozisyon=P("Müdür"))
        self.muhendis = Kullanici.objects.create_user("muh", password="x", first_name="Emirhan", pozisyon=P("Mühendis"))
        self.formen = Kullanici.objects.create_user("formen", password="x", pozisyon=P("Formen"), atolye=self.elk)
        self.ali = Kullanici.objects.create_user("ali", password="x", first_name="Ali", pozisyon=P("Personel"), atolye=self.elk)
        self.veli = Kullanici.objects.create_user("veli", password="x", pozisyon=P("Personel"), atolye=self.mek)

    def _yeni(self, kisi, **ek):
        self.client.force_login(kisi)
        veri = {"baslik": "Motor sargı ölçümü", "atolye": self.elk.pk, "oncelik": "NORMAL", "son_tarih": zaman(8)}
        veri.update(ek)
        return self.client.post(reverse("is_yeni"), veri)

    def _islem(self, kisi, is_, eylem, **ek):
        self.client.force_login(kisi)
        return self.client.post(reverse("is_islem", args=[is_.pk]), {"eylem": eylem, **ek})

    def test_muhendis_is_acar_formene_bildirim_gider(self):
        self._yeni(self.muhendis)
        is_ = Is.objects.get()
        self.assertEqual(is_.durum, Durum.ATANMADI)
        self.assertTrue(Bildirim.objects.filter(alici=self.formen, gorev=is_).exists())

    def test_personel_is_acamaz(self):
        self.assertEqual(self._yeni(self.ali).status_code, 403)

    def test_muhendis_acarken_kisi_atar(self):
        self._yeni(self.muhendis, sorumlu=self.ali.pk)
        is_ = Is.objects.get()
        self.assertEqual((is_.durum, is_.sorumlu), (Durum.ATANDI, self.ali))
        self.assertTrue(Bildirim.objects.filter(alici=self.ali).exists())

    def test_baska_atolyeden_kisi_atanamaz(self):
        r = self._yeni(self.muhendis, sorumlu=self.veli.pk)
        self.assertContains(r, "bu atölyede değil")

    def test_tam_akis(self):
        self._yeni(self.mudur)
        is_ = Is.objects.get()
        self._islem(self.formen, is_, "ata", sorumlu=self.ali.pk)
        is_.refresh_from_db()
        self.assertEqual(is_.durum, Durum.ATANDI)
        self._islem(self.ali, is_, "basla")
        is_.refresh_from_db()
        self.assertEqual(is_.durum, Durum.DEVAM)
        self._islem(self.ali, is_, "bitir", notu="Sargı sağlam")
        is_.refresh_from_db()
        self.assertEqual(is_.durum, Durum.TAMAMLANDI)
        self.assertTrue(Bildirim.objects.filter(alici=self.mudur, metin__contains="onay bekliyor").exists())
        # Personel kendi işini onaylayamaz
        self.assertEqual(self._islem(self.ali, is_, "onayla").status_code, 403)
        self._islem(self.mudur, is_, "onayla")
        is_.refresh_from_db()
        self.assertEqual(is_.durum, Durum.ONAYLANDI)
        self.assertEqual(is_.hareketler.count(), 5)

    def test_geri_gonder(self):
        self._yeni(self.muhendis, sorumlu=self.ali.pk)
        is_ = Is.objects.get()
        self._islem(self.ali, is_, "bitir")
        self._islem(self.muhendis, is_, "geri", notu="Rapor eksik")
        is_.refresh_from_db()
        self.assertEqual(is_.durum, Durum.DEVAM)

    def test_baska_atolyenin_personeli_isi_goremez(self):
        self._yeni(self.muhendis)
        is_ = Is.objects.get()
        self.client.force_login(self.veli)
        self.assertEqual(self.client.get(reverse("is_detay", args=[is_.pk])).status_code, 403)
        self.client.force_login(self.ali)
        self.assertEqual(self.client.get(reverse("is_detay", args=[is_.pk])).status_code, 200)

    def test_suresi_dolan_is_bildirilir_bir_kez(self):
        self._yeni(self.muhendis, sorumlu=self.ali.pk)
        is_ = Is.objects.get()
        Is.objects.filter(pk=is_.pk).update(son_tarih=timezone.now() - datetime.timedelta(minutes=1))
        self.client.force_login(self.ali)
        r = self.client.get(reverse("bildirim_durumu")).json()
        self.assertIn("Süresi doldu", r["son_metin"])
        self.client.get(reverse("bildirim_durumu"))
        self.assertEqual(Bildirim.objects.filter(metin__startswith="Süresi doldu", alici=self.ali).count(), 1)
        self.assertEqual(Bildirim.objects.filter(metin__startswith="Süresi doldu", alici=self.muhendis).count(), 1)

    def test_liste_sekmeleri(self):
        self._yeni(self.muhendis, sorumlu=self.ali.pk, baslik="ALININ ISI")
        self.client.force_login(self.ali)
        r = self.client.get(reverse("is_listesi"))
        self.assertEqual(r.context["sekme"], "bana")
        self.assertContains(r, "ALININ ISI")
        self.client.force_login(self.veli)
        self.assertNotContains(self.client.get(reverse("is_listesi") + "?sekme=acik"), "ALININ ISI")

    def test_detay_acilinca_bildirim_okunur(self):
        self._yeni(self.muhendis, sorumlu=self.ali.pk)
        is_ = Is.objects.get()
        self.client.force_login(self.ali)
        self.client.get(reverse("is_detay", args=[is_.pk]))
        self.assertFalse(Bildirim.objects.filter(alici=self.ali, okundu=False).exists())

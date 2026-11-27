import datetime
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from hesaplar.models import Atolye, Kullanici, Pozisyon

from .models import ArizaKaydi, Durum, Vardiya, simdiki_vardiya

IST = ZoneInfo("Europe/Istanbul")


class VardiyaSaatleri(TestCase):
    def test_vardiya_saatleri(self):
        self.assertEqual(simdiki_vardiya(datetime.datetime(2026, 1, 1, 3, 0, tzinfo=IST)), Vardiya.GECE)
        self.assertEqual(simdiki_vardiya(datetime.datetime(2026, 1, 1, 8, 0, tzinfo=IST)), Vardiya.SABAH)
        self.assertEqual(simdiki_vardiya(datetime.datetime(2026, 1, 1, 15, 59, tzinfo=IST)), Vardiya.SABAH)
        self.assertEqual(simdiki_vardiya(datetime.datetime(2026, 1, 1, 16, 0, tzinfo=IST)), Vardiya.AKSAM)


class DefterTestleri(TestCase):
    def setUp(self):
        self.elk = Atolye.objects.get(kod="ELK")
        self.mek = Atolye.objects.get(kod="MEK")
        personel = Pozisyon.objects.get(ad="Personel")
        self.ali = Kullanici.objects.create_user("ali", password="x", first_name="Ali", pozisyon=personel, atolye=self.elk)
        self.veli = Kullanici.objects.create_user("veli", password="x", first_name="Veli", pozisyon=personel, atolye=self.mek)
        self.muhendis = Kullanici.objects.create_user("ayse", password="x", pozisyon=Pozisyon.objects.get(ad="Mühendis"))

    def _kayit(self, kisi, atolye, **ek):
        veri = dict(atolye=atolye, postabasi=kisi, olusturan=kisi, ekipman="Pres 3", ariza="Motor ısındı", yapilan_is="Fan değişti")
        veri.update(ek)
        return ArizaKaydi.objects.create(**veri)

    def test_personel_kayit_ekler_kendi_atolyesine(self):
        self.client.force_login(self.ali)
        r = self.client.post(reverse("kayit_ekle"), {
            "tarih": timezone.localdate().isoformat(), "vardiya": 2, "atolye": self.mek.pk,  # başka atölye denemesi
            "postabasi": self.ali.pk, "ekipman": "Konveyör", "ariza": "Sensör arızası", "yapilan_is": "",
            "durum": Durum.DEVAM, "notlar": "Yedek sensör sipariş edildi",
        })
        self.assertEqual(r.status_code, 200)  # başka atölyeye kayıt açamaz
        r = self.client.post(reverse("kayit_ekle"), {
            "tarih": timezone.localdate().isoformat(), "vardiya": 2, "atolye": self.elk.pk,
            "postabasi": self.ali.pk, "ekipman": "Konveyör", "ariza": "Sensör arızası", "yapilan_is": "",
            "durum": Durum.DEVAM, "notlar": "Yedek sensör sipariş edildi",
        })
        self.assertRedirects(r, reverse("defter"))
        k = ArizaKaydi.objects.get()
        self.assertEqual((k.atolye, k.olusturan, k.notlar), (self.elk, self.ali, "Yedek sensör sipariş edildi"))
        self.assertIsNone(k.kapatan)

    def test_tamamlanan_is_icin_yapilan_is_zorunlu(self):
        self.client.force_login(self.ali)
        r = self.client.post(reverse("kayit_ekle"), {
            "tarih": timezone.localdate().isoformat(), "vardiya": 1, "atolye": self.elk.pk, "postabasi": self.ali.pk,
            "ekipman": "X", "ariza": "Y", "yapilan_is": "", "durum": Durum.BITTI,
        })
        self.assertContains(r, "yapılan işi yazın")

    def test_personel_sadece_kendi_atolyesini_gorur(self):
        self._kayit(self.ali, self.elk, ekipman="ELK-ISI")
        self._kayit(self.veli, self.mek, ekipman="MEK-ISI")
        self.client.force_login(self.ali)
        r = self.client.get(reverse("defter"))
        self.assertContains(r, "ELK-ISI")
        self.assertNotContains(r, "MEK-ISI")
        self.client.force_login(self.muhendis)
        r = self.client.get(reverse("defter"))
        self.assertContains(r, "ELK-ISI")
        self.assertContains(r, "MEK-ISI")

    def test_devreden_is_ustte_ve_kapatilir(self):
        dun = timezone.localdate() - datetime.timedelta(days=1)
        k = self._kayit(self.ali, self.elk, tarih=dun, durum=Durum.DEVAM, yapilan_is="", ekipman="DEVREDEN")
        self.client.force_login(self.ali)
        r = self.client.get(reverse("defter"))
        self.assertEqual(list(r.context["acik"]), [k])
        self.client.post(reverse("kayit_kapat", args=[k.pk]), {"yapilan_is": "Rulman değişti"})
        k.refresh_from_db()
        self.assertEqual(k.durum, Durum.BITTI)
        self.assertEqual(k.kapatan, self.ali)
        self.assertIn("Rulman değişti", k.yapilan_is)

    def test_baska_atolyenin_kaydini_duzenleyemez(self):
        k = self._kayit(self.veli, self.mek, durum=Durum.DEVAM)
        self.client.force_login(self.ali)
        self.assertEqual(self.client.get(reverse("kayit_duzenle", args=[k.pk])).status_code, 403)
        self.client.post(reverse("kayit_kapat", args=[k.pk]), {"yapilan_is": "x"})
        k.refresh_from_db()
        self.assertEqual(k.durum, Durum.DEVAM)

    def test_tarihe_gore_gezinme(self):
        dun = timezone.localdate() - datetime.timedelta(days=1)
        self._kayit(self.ali, self.elk, tarih=dun, ekipman="DUNKU")
        self.client.force_login(self.ali)
        self.assertNotContains(self.client.get(reverse("defter")), "DUNKU")
        self.assertContains(self.client.get(reverse("defter") + f"?tarih={dun.isoformat()}"), "DUNKU")

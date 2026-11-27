from django import forms

from hesaplar.models import Atolye, Kullanici

from .models import ArizaKaydi, Durum


class ArizaFormu(forms.ModelForm):
    class Meta:
        model = ArizaKaydi
        fields = ["tarih", "vardiya", "atolye", "postabasi", "ekipman", "ariza", "yapilan_is", "durum", "notlar"]
        widgets = {
            "tarih": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "ariza": forms.Textarea(attrs={"rows": 3, "placeholder": "Ne oldu?"}),
            "yapilan_is": forms.Textarea(attrs={"rows": 3, "placeholder": "Ne yapıldı? Devam ediyorsa nerede kalındı?"}),
            "notlar": forms.Textarea(attrs={"rows": 2, "placeholder": "Sonraki vardiyaya veya yöneticilere not (isteğe bağlı)"}),
            "ekipman": forms.TextInput(attrs={"placeholder": "Ör. Pres 3, Konveyör B hattı"}),
            "durum": forms.RadioSelect,
        }

    def __init__(self, *args, kullanici=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.kullanici = kullanici
        atolyeler = Atolye.objects.filter(aktif=True)
        kisiler = Kullanici.objects.filter(is_active=True, pozisyon__isnull=False)
        if kullanici.tum_atolyeleri_gorur:
            self.fields["atolye"].queryset = atolyeler
        else:
            # Kendi atölyesi dışında kayıt açamaz; alanı gizle
            self.fields["atolye"].queryset = atolyeler.filter(pk=kullanici.atolye_id)
            self.fields["atolye"].initial = kullanici.atolye_id
            self.fields["atolye"].widget = forms.HiddenInput()
            kisiler = kisiler.filter(atolye_id=kullanici.atolye_id)
        self.fields["postabasi"].queryset = kisiler.order_by("first_name")
        self.fields["atolye"].empty_label = "Seçiniz"
        self.fields["postabasi"].empty_label = "Seçiniz"
        self.fields["durum"].choices = Durum.choices
        if not self.instance.pk and kullanici.atolye_id:
            self.fields["atolye"].initial = kullanici.atolye_id
            self.fields["postabasi"].initial = kullanici.pk

    def clean(self):
        veri = super().clean()
        if veri.get("durum") == Durum.BITTI and not veri.get("yapilan_is"):
            self.add_error("yapilan_is", "Tamamlanan iş için yapılan işi yazın.")
        return veri

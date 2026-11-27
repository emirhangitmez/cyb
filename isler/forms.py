import datetime

from django import forms
from django.utils import timezone

from hesaplar.models import Atolye, Kullanici, Yetki

from .models import Is


class IsFormu(forms.ModelForm):
    class Meta:
        model = Is
        fields = ["baslik", "atolye", "ekipman", "aciklama", "oncelik", "son_tarih", "sorumlu"]
        widgets = {
            "baslik": forms.TextInput(attrs={"placeholder": "Ör. Pres 3 motor sargı ölçümü yapılacak"}),
            "aciklama": forms.Textarea(attrs={"rows": 3, "placeholder": "Detay (isteğe bağlı)"}),
            "son_tarih": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "oncelik": forms.RadioSelect,
        }
        labels = {"sorumlu": "Kişi ata (isteğe bağlı)"}

    def __init__(self, *args, kullanici=None, **kwargs):
        super().__init__(*args, **kwargs)
        atolyeler = Atolye.objects.filter(aktif=True)
        if not kullanici.tum_atolyeleri_gorur:
            # Mühendis ve formen sadece kendi atölyesine iş açar
            atolyeler = atolyeler.filter(pk=kullanici.atolye_id)
        self.fields["atolye"].queryset = atolyeler
        self.fields["atolye"].empty_label = "Seçiniz"
        if not self.instance.pk:
            self.fields["son_tarih"].initial = (timezone.localtime() + datetime.timedelta(hours=8)).replace(minute=0, second=0, microsecond=0)
            if kullanici.atolye_id:
                self.fields["atolye"].initial = kullanici.atolye_id
        kisiler = Kullanici.objects.filter(is_active=True, pozisyon__yetki__in=[Yetki.PERSONEL, Yetki.FORMEN])
        if not kullanici.gorev_atayabilir:
            del self.fields["sorumlu"]
        else:
            if not kullanici.tum_atolyeleri_gorur:
                kisiler = kisiler.filter(atolye_id=kullanici.atolye_id)
            self.fields["sorumlu"].queryset = kisiler.select_related("atolye").order_by("atolye__ad", "first_name")
            self.fields["sorumlu"].label_from_instance = lambda k: f"{k} ({k.atolye.kod if k.atolye else '-'})"
            self.fields["sorumlu"].empty_label = "Şimdilik atama (formen atasın)"

    def clean(self):
        veri = super().clean()
        sorumlu, atolye = veri.get("sorumlu"), veri.get("atolye")
        if sorumlu and atolye and sorumlu.atolye_id != atolye.pk:
            self.add_error("sorumlu", f"{sorumlu} bu atölyede değil.")
        if not self.instance.pk and veri.get("son_tarih") and veri["son_tarih"] < timezone.now():
            self.add_error("son_tarih", "Bitiş süresi geçmiş bir zaman olamaz.")
        return veri

# Vardiya Takip ve Görev Listesi

Bakım atölyeleri (Elektrik / Mekanik) için vardiya defteri ve iş isteği / görev takip uygulaması.
Fabrikanın iç ağındaki bir bilgisayarda çalışır; diğer bilgisayarlardan tarayıcı ile girilir.

## Durum

- [x] **1. adım:** Giriş sistemi ve admin paneli (kişiler, görevler, atölyeler)
- [x] **2. adım:** Vardiya defteri (arıza kayıtları, postabaşı, notlar, devreden işler)
- [x] **3. adım:** İş istekleri ve görevler (atama, süre, otomatik yenilenen liste, bildirim)
- [ ] **4. adım:** Sunucu kurulumu, otomatik yedek, kullanım kılavuzu

## Admin paneli

Admin (`/panel/`) şunları yönetir:
- **Görevler:** Müdür, Mühendis, Formen, Personel hazır gelir. Yeni görev eklenebilir (ör. Postabaşı) ve her görev bir yetki seviyesine bağlanır.
- **Atölyeler:** Elektrik ve Mekanik hazır gelir. Yeni atölye eklenebilir.
- **Kişiler:** Ad soyad, kullanıcı adı (giriş ID), şifre, görev ve atölye atanır. Şifre sıfırlama, pasif yapma.

| Yetki seviyesi | Ne yapabilir |
|---|---|
| Müdür | Tüm atölyeleri görür, iş açar, personel atar, onay hakkı vardır. Sadece kendi açtığı iş bitince bildirim alır |
| Mühendis | Kendi atölyesine bağlıdır (ör. elektrik bakım mühendisi). O atölyede iş açar, personel atar, biten işleri onaylar |
| Formen | Kendi atölyesinde iş açar ve personel atar |
| Personel | Kendi atölyesinin vardiya defterini yazar, kendisine atanan görevleri günceller |

## Vardiya defteri

`/vardiya/` sayfası tek ekrandır:
- **Üstte devreden açık işler:** Önceki vardiyalardan "Devam ediyor" olarak bırakılan işler. Yapılan işi yazıp **Tamamlandı** demek yeterli.
- **Altta günün kayıtları:** Vardiyalara (00-08, 08-16, 16-24) göre gruplanır, gün gün geriye gidilebilir.
- Her kayıtta: tarih, vardiya, atölye, postabaşı, makine/hat, arıza, yapılan iş, durum ve not.
- Personel ve formen sadece kendi atölyesini görür; müdür ve mühendis tümünü görür.
- Sayfa 30 saniyede bir kendini yeniler (kullanıcı yazı yazarken yenilenmez).

## İşler (iş istekleri ve görevler)

`/isler/` sayfası:
- **Müdür, mühendis veya formen** iş isteği açar (mühendis ve formen sadece kendi atölyesine): ne yapılacak, atölye, makine, bitiş süresi, öncelik (Normal/Acil). İsterse kişiyi de hemen atar; atamazsa atölyenin formenine bildirim gider.
- **Müdür, mühendis ve formen** işe personel atayabilir veya kişiyi değiştirebilir.
- **Atanan kişi** "İşe başladım" ve "İş bitti" der.
- **Atölyenin mühendisi** "Onayla ve kapat" ya da "Geri gönder" der. Müdürün de onay hakkı vardır ama beklenmez; formen onaylamaz.
- Durumlar: Kişi bekliyor → Atandı → Devam ediyor → Onay bekliyor → Onaylandı.
- Süresi dolan iş kırmızı görünür; atanan kişiye, işi açana, atölye formenine ve mühendisine bildirim gider.
- Müdüre ara aşamalarda bildirim gitmez; sadece kendi açtığı iş onaylanıp bitince haber verilir.
- Üstteki 🔔 zil 15 saniyede bir kontrol edilir; yeni bildirim gelince sağ altta kısa bir uyarı çıkar.
- Her işin altında geçmiş ve not alanı vardır.

## Bilgisayarda deneme (Windows)

Python 3.11 veya üstü kurulu olmalı.

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py ornek_kullanicilar
python manage.py runserver 0.0.0.0:8000
```

Tarayıcıda `http://localhost:8000` açın. Örnek kullanıcılar (şifre `123456`):
`admin`, `mudur`, `elektrik.muhendis`, `mekanik.muhendis`, `elektrik.formen`, `mekanik.formen`, `elektrik.personel`, `mekanik.personel`.

Gerçek kullanımda örnek kullanıcılar yerine `python manage.py createsuperuser` ile admin hesabını
oluşturun, diğer kişileri **Admin paneli > Kişiler** sayfasından ekleyin.

Testler: `python manage.py test`

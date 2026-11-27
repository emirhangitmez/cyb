# Vardiya Takip ve Görev Listesi

Bakım atölyeleri (Elektrik / Mekanik) için vardiya defteri ve iş isteği / görev takip uygulaması.
Fabrikanın iç ağındaki bir bilgisayarda çalışır; diğer bilgisayarlardan tarayıcı ile girilir.

## Durum

- [x] **1. adım:** Giriş sistemi ve admin paneli (kişiler, görevler, atölyeler)
- [x] **2. adım:** Vardiya defteri (arıza kayıtları, postabaşı, notlar, devreden işler)
- [ ] **3. adım:** İş istekleri ve görevler (atama, süre, otomatik yenilenen liste, bildirim)
- [ ] **4. adım:** Sunucu kurulumu, otomatik yedek, kullanım kılavuzu

## Admin paneli

Admin (`/panel/`) şunları yönetir:
- **Görevler:** Müdür, Mühendis, Formen, Personel hazır gelir. Yeni görev eklenebilir (ör. Postabaşı) ve her görev bir yetki seviyesine bağlanır.
- **Atölyeler:** Elektrik ve Mekanik hazır gelir. Yeni atölye eklenebilir.
- **Kişiler:** Ad soyad, kullanıcı adı (giriş ID), şifre, görev ve atölye atanır. Şifre sıfırlama, pasif yapma.

| Yetki seviyesi | Ne yapabilir |
|---|---|
| Müdür | Her şeyi görür, iş isteği oluşturur, işe personel atar |
| Mühendis | Tüm atölyeleri görür, iş isteği oluşturur, işe personel atar |
| Formen | Kendi atölyesini görür, iş isteği oluşturur, işe personel atar |
| Personel | Kendi atölyesinin vardiya defterini yazar, kendisine atanan görevleri günceller |

## Vardiya defteri

`/vardiya/` sayfası tek ekrandır:
- **Üstte devreden açık işler:** Önceki vardiyalardan "Devam ediyor" olarak bırakılan işler. Yapılan işi yazıp **Tamamlandı** demek yeterli.
- **Altta günün kayıtları:** Vardiyalara (00-08, 08-16, 16-24) göre gruplanır, gün gün geriye gidilebilir.
- Her kayıtta: tarih, vardiya, atölye, postabaşı, makine/hat, arıza, yapılan iş, durum ve not.
- Personel ve formen sadece kendi atölyesini görür; müdür ve mühendis tümünü görür.
- Sayfa 30 saniyede bir kendini yeniler (kullanıcı yazı yazarken yenilenmez).

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
`admin`, `mudur`, `muhendis`, `elektrik.formen`, `mekanik.formen`, `elektrik.personel`, `mekanik.personel`.

Gerçek kullanımda örnek kullanıcılar yerine `python manage.py createsuperuser` ile admin hesabını
oluşturun, diğer kişileri **Admin paneli > Kişiler** sayfasından ekleyin.

Testler: `python manage.py test`

# Vardiya Takip ve Görev Listesi

Bakım atölyeleri (Elektrik / Mekanik) için vardiya defteri ve iş isteği / görev takip uygulaması.
Fabrikanın iç ağındaki bir bilgisayarda çalışır; diğer bilgisayarlardan tarayıcı ile girilir.

## Durum

- [x] **1. adım:** Giriş sistemi, roller (Müdür, Mühendis, Formen, Personel), atölyeler, kullanıcı yönetimi
- [ ] **2. adım:** Vardiya defteri (arıza kayıtları, postabaşı, notlar, devreden işler)
- [ ] **3. adım:** İş istekleri ve görevler (atama, süre, otomatik yenilenen liste, bildirim)
- [ ] **4. adım:** Sunucu kurulumu, otomatik yedek, kullanım kılavuzu

## Roller

| Rol | Yetkiler |
|---|---|
| Müdür | Her şeyi görür, kullanıcı ekler/düzenler, iş isteği oluşturur, görev atayabilir |
| Mühendis | Tüm atölyeleri görür, iş isteği oluşturur |
| Formen | Kendi atölyesini görür, iş isteği oluşturur, atölyesindeki personele görev atar |
| Personel | Kendi atölyesinin vardiya defterini yazar, kendisine atanan görevleri günceller |

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
`mudur`, `muhendis`, `elektrik.formen`, `mekanik.formen`, `elektrik.personel`, `mekanik.personel`.

Gerçek kullanımda örnek kullanıcılar yerine `python manage.py createsuperuser` ile ilk müdür hesabını
oluşturun, diğer kullanıcıları uygulamadaki **Kullanıcılar** sayfasından ekleyin.

Testler: `python manage.py test`

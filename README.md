# Kapadokya AI - Üretim Verimlilik Sistemi (ÜVS)

Bu proje, yapay zeka ve görüntü işleme teknolojilerini kullanarak inşaat ve üretim alanlarında verimlilik, iş güvenliği ve kalite kontrolü sağlayan bir sistemdir.

## Proje Bileşenleri

Proje iki ana bileşenden oluşmaktadır:

1. **Backend** - Django ve REST API
   - YOLOv11 entegrasyonu
   - Görüntü işleme algoritmaları
   - Verimlilik hesaplamaları
   - Rapor oluşturma

2. **Frontend** - React.js
   - Dashboard ve veri görselleştirme
   - Alarm ve bildirim sistemi
   - Kullanıcı arayüzü

## Desteklenen Özellikler

### İSG (İş Sağlığı ve Güvenliği)
- Alan İçine Giren İşçi Tespiti 
- Tehlikeli Alan Tespiti
- Ekipman Kontrolü (Baret, Gözlük, Eldiven, vb.)

### Verim Sistemi
- İşçi Odak Görüntüleme
- İşçi Hareket Görüntüleme (Isı Haritası)
- Verimlilik Metrikleri

### Üretim Takibi
- Ürün Sayımı
- Kalite Kontrolü
- Üretim Hattı Optimizasyonu

### Raporlama
- Günlük, Haftalık, Aylık Raporlar
- Trend Analizi
- Yapay Zeka Destekli Tavsiyeleri
- Anomali Tespiti

## Teknik Altyapı

- **Backend**: Django 4.2 ve Django REST Framework
- **Görüntü İşleme**: OpenCV ve YOLOv11
- **Görev Yönetimi**: Celery ve Redis
- **Veritabanı**: PostgreSQL
- **Frontend**: React.js ve Recharts

## Kurulum

Kurulum talimatları için `backend/birlesim_talimatlari.txt` dosyasını inceleyiniz.

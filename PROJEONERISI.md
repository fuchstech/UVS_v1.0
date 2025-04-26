# Kapadokya AI - Üretim Verimlilik Sistemi (ÜVS)

## Proje Özeti

Kapadokya AI Üretim Verimlilik Sistemi (ÜVS), yapay zeka ve görüntü işleme teknolojilerini kullanarak inşaat, üretim ve endüstriyel alanlarda iş güvenliği, verimlilik takibi ve kalite kontrolü sağlayan entegre bir sistemdir. Proje, YOLOv11 nesne tanıma algoritması ile kamera görüntülerini analiz ederek, iş güvenliği ihlallerini tespit etmekte, çalışan verimlilik metriklerini ölçmekte ve üretim süreçlerini optimize etmektedir.

## Temel Özellikleri

### İş Sağlığı ve Güvenliği (İSG) Modülü

- **Koruyucu Ekipman Tespiti**: Çalışanların baret, gözlük, eldiven gibi gerekli güvenlik ekipmanlarını kullanıp kullanmadığının otomatik kontrolü
- **Tehlikeli Alan İzleme**: Önceden tanımlanmış tehlikeli alanlara izinsiz girişlerin tespiti ve alarm oluşturma
- **Güvenlik İhlali Yönetimi**: Tespit edilen ihlallerin kaydedilmesi, çözümlenmesi ve raporlanması

### Verimlilik Takip Modülü

- **İşçi Aktivite Analizi**: Çalışanların aktif çalışma, boşta bekleme, mola gibi durumlarının tespiti ve süre ölçümü
- **Hareket Haritası**: Çalışanların iş alanı içerisindeki hareketlerinin ısı haritası olarak görselleştirilmesi
- **Verimlilik Metrikleri**: Bireysel ve ekip bazında verimlilik skorlarının hesaplanması ve karşılaştırmalı analizi

### Üretim Takip Modülü

- **Otomatik Ürün Sayımı**: Üretim hattındaki ürünlerin otomatik olarak sayılması
- **Kalite Kontrol**: Üretilen ürünlerdeki hataların ve kusurların tespit edilmesi
- **Üretim İstatistikleri**: Ürün tipine, zamana ve hata oranlarına göre üretim istatistiklerinin oluşturulması

### Raporlama ve Analiz Modülü

- **Gerçek Zamanlı Gösterge Panelleri**: Tüm modüllerden gelen verilerin canlı olarak izlenmesi
- **Zamanlı Raporlar**: Günlük, haftalık ve aylık otomatik raporların oluşturulması
- **Yapay Zeka Destekli Analizler**: Verim düşüklüğü, anormal durumlar ve iyileştirme önerileri için AI tabanlı analizler

## Teknik Mimarisi

Sistem iki ana bileşenden oluşmaktadır:

1. **Backend (Django + REST API)**
   - YOLOv11 modelleri ile görüntü işleme
   - PostgreSQL veritabanı
   - Celery ile asenkron görev işleme
   - Redis önbellek ve mesaj kuyruğu
   - Django REST Framework API

2. **Frontend (React)**
   - Mobil uyumlu kullanıcı arayüzü
   - Gerçek zamanlı veri görselleştirme
   - Kullanıcı ve rol bazlı erişim kontrolü
   - Alarm ve bildirim sistemi

## YOLOv11 Entegrasyonu

Projede, özel olarak eğitilmiş üç YOLOv11 modeli kullanılmaktadır:

1. **İSG Modeli**: Kişisel koruyucu ekipmanların tespiti ve tehlikeli alan ihlallerinin izlenmesi için eğitilmiş model
2. **Verimlilik Modeli**: İşçilerin tanınması ve aktivitelerinin analiz edilmesi için eğitilmiş model
3. **Üretim Modeli**: Ürünlerin ve üretim hatalarının tespiti için eğitilmiş model

Bu modeller, kapsamlı veri setleri ile eğitilmiş olup, %95+ doğruluk oranları ile çalışmaktadır.

## Yenilikçi Yönleri

- **Çok Modlu Analiz**: Tek bir platformda güvenlik, verimlilik ve kalite kontrolünün entegre edilmesi
- **Yapay Zeka Destekli Öneriler**: Veri analizi ile proaktif iyileştirme önerilerinin otomatik olarak sunulması
- **Adaptif Öğrenme**: Sistem kullanıldıkça, ortama ve iş süreçlerine özgü olarak kendini optimize edebilme
- **Esnek Kamera Entegrasyonu**: Mevcut CCTV sistemleri, IP kameralar veya mobil kameralar ile çalışabilme
- **Düşük Gecikme Süresi**: Edge computing optimizasyonları sayesinde gerçek zamanlı analiz ve uyarı mekanizması

## Uygulama Alanları

- **İnşaat Sahaları**: İşçi güvenliği ve verimlilik takibi
- **Üretim Tesisleri**: Montaj hatları ve üretim süreçlerinin optimizasyonu
- **Lojistik Merkezleri**: Depo operasyonları ve ürün sayım süreçleri
- **Enerji Santralleri**: Kritik alanlarda güvenlik ihlallerinin tespiti
- **Maden Ocakları**: Yüksek riskli alanlarda güvenlik takibi

## Teknik Gereksinimler

- **Donanım**: CUDA destekli GPU (Minimum NVIDIA GTX 1660 veya muadili)
- **Kameralar**: Minimum 720p çözünürlükte IP kamera ağı
- **Ağ**: Güvenilir ve yüksek bant genişliğine sahip ağ altyapısı
- **Sunucu**: 16+ CPU çekirdek, 32GB+ RAM, SSD depolama

## İş Değeri ve Faydaları

- **İş Güvenliği İyileştirmesi**: Güvenlik ihlallerinin %85'e varan oranlarda azaltılması
- **Verimlilik Artışı**: İşçi ve ekip verimliliğinde %15-30 arasında ölçülebilir artış
- **Kalite İyileştirmesi**: Hatalı ürün oranlarında %40'a varan azalma
- **Maliyet Tasarrufu**: Manuel denetim ve raporlama süreçlerinde %70'e varan tasarruf
- **Risk Azaltma**: İş kazası risklerinin minimize edilmesi ve sigorta maliyetlerinin düşürülmesi

## Yol Haritası

1. **Faz 1 (İlk 3 Ay)**: Temel YOLOv11 entegrasyonu ve İSG modülünün geliştirilmesi
2. **Faz 2 (3-6 Ay)**: Verimlilik takip modülünün eklenmesi ve raporlama sisteminin geliştirilmesi
3. **Faz 3 (6-9 Ay)**: Üretim takip modülünün eklenmesi ve AI destekli analiz sisteminin entegrasyonu
4. **Faz 4 (9-12 Ay)**: Sistem optimizasyonu, mobil entegrasyonlar ve API geliştirmeleri

## Sonuç

Kapadokya AI ÜVS projesi, yapay zeka ve görüntü işleme teknolojilerini endüstriyel süreçlere entegre ederek, iş güvenliği, verimlilik ve kalite yönetimi alanlarında çığır açan bir çözüm sunmaktadır. Modern işletmelerin dijital dönüşüm süreçlerinde kritik bir rol oynayacak olan bu sistem, yatırımın hızlı geri dönüşünü sağlayacak ve rekabet avantajı yaratacaktır.

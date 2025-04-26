# Kapadokya AI - Kurulum Talimatları

Bu belge, Kapadokya AI Üretim Verimlilik Sistemi (ÜVS) projesinin kurulum adımlarını detaylı olarak açıklamaktadır.

## Gereksinimler

### Temel Gereksinimler
- Python 3.9+
- Node.js 16+ ve npm 8+
- PostgreSQL 14+
- Redis Server
- CUDA destekli bir GPU (YOLOv11 modelleri için)

### Python Paketleri
Gerekli Python paketleri `requirements.txt` dosyasında listelenmiştir.

### YOLOv11 Modelleri
Sistem aşağıdaki eğitilmiş YOLOv11 modellerini kullanmaktadır:
- `isg_model.pt` - İş güvenliği ekipmanları tespiti için (baret, gözlük, eldiven, vb.)
- `worker_activity_model.pt` - İşçi aktivite tespiti için
- `product_detection_model.pt` - Ürün sayımı ve kalite kontrolü için

## Backend Kurulumu

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/your-username/kapadokya-ai.git
   cd kapadokya-ai
   ```

2. Python sanal ortamı oluşturun ve aktifleştirin:
   ```bash
   python -m venv venv
   # Windows için
   venv\Scripts\activate
   # Linux/Mac için
   source venv/bin/activate
   ```

3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. PostgreSQL veritabanı oluşturun:
   ```bash
   createdb kapadokya_ai
   ```

5. Environment değişkenlerini ayarlayın (veya `.env` dosyası oluşturun):
   ```
   DATABASE_URL=postgresql://username:password@localhost/kapadokya_ai
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   REDIS_URL=redis://localhost:6379/0
   ```

6. YOLOv11 modellerini yerleştirin:
   - Eğitilmiş model dosyalarını `backend/kapadokya_project/ai_models/yolov11_models/` dizinine kopyalayın:
     - `isg_model.pt`
     - `worker_activity_model.pt`
     - `product_detection_model.pt`

7. Veritabanı migrasyonlarını uygulayın:
   ```bash
   cd backend
   python manage.py migrate
   ```

8. Bir süper kullanıcı oluşturun:
   ```bash
   python manage.py createsuperuser
   ```

9. Statik dosyaları toplayın:
   ```bash
   python manage.py collectstatic
   ```

10. Django sunucusunu başlatın:
    ```bash
    python manage.py runserver
    ```

11. Celery worker'ı başlatın (ayrı bir terminalde):
    ```bash
    celery -A kapadokya_project worker -l info
    ```

12. Celery beat zamanlanmış görevler için (ayrı bir terminalde):
    ```bash
    celery -A kapadokya_project beat -l info
    ```

## Frontend Kurulumu

1. Frontend dizinine gidin:
   ```bash
   cd frontend
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   npm install
   ```

3. Environment değişkenlerini ayarlayın (`.env.local` dosyası oluşturun):
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

4. Geliştirme sunucusunu başlatın:
   ```bash
   npm start
   ```

5. Üretim (production) build oluşturmak için:
   ```bash
   npm run build
   ```

## Sistem Mimarisi

### Backend Bileşenleri

1. **Django ve Django REST Framework**: Ana API ve uygulama mantığı
2. **PostgreSQL**: Veri saklama
3. **Redis**: Önbellek ve Celery broker'ı
4. **Celery**: Asenkron görevler ve zamanlayıcı
5. **YOLOv11**: Görüntü işleme ve nesne tanıma

### Frontend Bileşenleri

1. **React**: Kullanıcı arayüzü
2. **Redux**: Durum yönetimi
3. **Recharts**: Veri görselleştirme
4. **Axios**: HTTP istekleri

## Kamera Entegrasyonu

Sistem aşağıdaki kamera türlerini desteklemektedir:

1. **IP Kameralar**: RTSP, HTTP veya MJPEG protokolleri ile
2. **USB Kameralar**: OpenCV aracılığıyla
3. **Statik Görüntüler**: Test amaçları için

Kamera kurulumu için:

1. Django admin paneline giriş yapın: `http://localhost:8000/admin/`
2. `Cameras` bölümüne gidin ve yeni kamera ekleyin
3. Kamera tipini ve bağlantı bilgilerini girin
4. Kamerayı ilgili alana atayın (İSG, Verimlilik veya Ürün Takibi)

## GPU Konfigürasyonu

YOLOv11 modelleri GPU kullanımı için optimizedir. CUDA kurulumu için:

1. NVIDIA grafik sürücülerinin güncel olduğundan emin olun
2. [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) yükleyin
3. [cuDNN](https://developer.nvidia.com/cudnn) yükleyin
4. PyTorch'un CUDA versiyonunu yükleyin:
   ```bash
   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
   ```

## Sorun Giderme

### Backend Sorunları

1. **Veritabanı Bağlantı Hataları**:
   - PostgreSQL servisinin çalıştığından emin olun
   - Veritabanı bağlantı bilgilerini kontrol edin

2. **YOLOv11 Model Hataları**:
   - Model dosyalarının doğru konumda olduğunu kontrol edin
   - CUDA sürümlerinin uyumlu olduğunu doğrulayın

3. **Celery Bağlantı Hataları**:
   - Redis servisinin çalıştığından emin olun
   - `REDIS_URL` değişkeninin doğru ayarlandığını kontrol edin

### Frontend Sorunları

1. **API Bağlantı Hataları**:
   - Backend API'nin çalıştığından emin olun
   - CORS ayarlarını kontrol edin
   - API URL'sinin doğru olduğunu doğrulayın

## Güvenlik Notları

1. Production ortamında `DEBUG=False` olarak ayarlayın
2. Güçlü bir `SECRET_KEY` kullanın
3. HTTPS kullanın
4. API erişimi için JWT token doğrulama kullanın
5. Parolaları ve hassas bilgileri environment değişkenlerinde saklayın

## Lisans ve Telif Hakkı

Bu proje, Kapadokya AI tarafından geliştirilmiştir ve tüm hakları saklıdır. İzinsiz kullanım, kopyalama veya dağıtım yapılamaz.

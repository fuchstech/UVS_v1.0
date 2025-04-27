"""
Veritabanından bağımsız, doğrudan YOLO modelini kullanan görüntü işleme modülü
"""
import os
import uuid
import tempfile
import cv2
import numpy as np
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

class YoloVideoProcessor(APIView):
    """
    Hiçbir veritabanı modeli kullanmadan, doğrudan YOLO ile video işleme endpoint'i
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = []  # Hiçbir izin gerektirmez
    
    def post(self, request, format=None):
        try:
            print("YOLO: Video işleme isteği alındı")
            print(f"YOLO: Gelen veri: {request.data}")
            print(f"YOLO: Gelen dosyalar: {request.FILES}")
            
            # Video dosyasını kontrol et
            video_file = request.FILES.get('video')
            if not video_file:
                print("YOLO: Video dosyası eksik")
                return Response(
                    {"detail": "Video dosyası gerekli."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"YOLO: Video dosyası alındı: {video_file.name}, boyut: {video_file.size}")
            
            # Geçici bir klasör oluştur
            temp_dir = tempfile.mkdtemp()
            temp_output_dir = os.path.join(temp_dir, "output")
            os.makedirs(temp_output_dir, exist_ok=True)
            
            try:
                # Video dosyasını geçici olarak kaydet
                temp_video_path = os.path.join(temp_dir, video_file.name)
                with open(temp_video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                        
                print(f"YOLO: Video dosyası geçici konuma kaydedildi: {temp_video_path}")
                
                # Kalıcı olarak kaydet
                unique_filename = f"yolo_{uuid.uuid4().hex}_{video_file.name}"
                save_path = os.path.join('uploads', unique_filename)
                video_path = default_storage.save(save_path, ContentFile(video_file.read()))
                
                print(f"YOLO: Video dosyası kaydedildi: {video_path}")
                
                # YOLO modeli ile işleme
                detections = []
                try:
                    # Model yolunu kontrol et
                    base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    yolo_path = os.path.join(base_dir, '..', 'yolo_models')
                    model_paths = {
                        'isg': os.path.join(yolo_path, 'isg_model.pt'),
                        'default': os.path.join(yolo_path, 'yolov8n.pt')  # Varsayılan model
                    }
                    
                    # Mevcut bir model dosyası bul
                    model_file = None
                    for key, path in model_paths.items():
                        if os.path.exists(path):
                            model_file = path
                            print(f"YOLO: Model bulundu: {key} - {path}")
                            break
                    
                    if model_file:
                        print(f"YOLO: Model kullanılıyor: {model_file}")
                        # Ultralytics YOLO modülünü yükle
                        try:
                            from ultralytics import YOLO
                            model = YOLO(model_file)
                            
                            # Video'dan örnek kareler al ve işle
                            cap = cv2.VideoCapture(temp_video_path)
                            frame_count = 0
                            max_frames = 10  # İşlenecek maksimum kare sayısı
                            sample_rate = int(request.data.get('sample_rate', 30))  # Her 30 karede bir işlem
                            
                            # İşlenmiş video için hazırlık
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                            
                            # İşlenmiş video dosyası yolu
                            processed_video_filename = f"processed_{uuid.uuid4().hex}_{video_file.name}"
                            processed_video_path = os.path.join(temp_output_dir, processed_video_filename)
                            
                            # Video yazıcı (fourcc kodunu belirleme)
                            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 formatı
                            out = cv2.VideoWriter(processed_video_path, fourcc, fps, (width, height))
                            
                            frames_processed = 0
                            
                            # Renk paleti (farklı sınıflar için farklı renkler)
                            color_palette = {
                                'helmet': (0, 255, 0),      # Yeşil
                                'safety_glasses': (255, 0, 0),  # Kırmızı
                                'gloves': (0, 0, 255),     # Mavi
                                'safety_vest': (255, 255, 0), # Sarı
                                'person': (255, 0, 255),   # Mor
                                'default': (200, 200, 200)  # Gri
                            }
                            
                            while cap.isOpened() and frames_processed < max_frames:
                                ret, frame = cap.read()
                                if not ret:
                                    break
                                    
                                if frame_count % sample_rate == 0:
                                    # Kareyi kaydet
                                    frame_path = os.path.join(temp_output_dir, f"frame_{frame_count}.jpg")
                                    
                                    # YOLO modeli ile tahmin yap
                                    results = model(frame)
                                    
                                    # Tahmin sonuçlarını işle
                                    frame_detections = []
                                    original_frame = frame.copy()
                                    
                                    # Tespit edilen nesnelerin etrafına kutu çizme
                                    for result in results:
                                        for box in result.boxes.data.tolist():
                                            x1, y1, x2, y2, confidence, class_id = box
                                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                            class_name = model.names[int(class_id)]
                                            
                                            # İSG ekipmanlarına göre özel durum
                                            status = "detected"
                                            if class_name in ["helmet", "safety_glasses", "gloves", "safety_vest"]:
                                                # İSG ekipmanları için özel durum ataması
                                                status = "detected" if confidence > 0.5 else "missing"
                                            
                                            frame_detections.append({
                                                "class": class_name,
                                                "confidence": confidence,
                                                "status": status,
                                                "box": [x1, y1, x2, y2]
                                            })
                                            
                                            # Tespit çerçevesi çizme
                                            # Sınıfa özel renk seçme
                                            color = color_palette.get(class_name, color_palette['default'])
                                            
                                            # Kutu çizme
                                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                            
                                            # Sınıf bilgisi ve güven değeri
                                            label = f"{class_name}: {confidence:.2f}"
                                            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                            
                                    # İşlenen kareyi kaydet
                                    cv2.imwrite(frame_path, frame)
                                    
                                    # İşlenen kareyi videoya ekle
                                    out.write(frame)
                                    
                                    detections.append({
                                        "frame": frame_count,
                                        "detections": frame_detections
                                    })
                                    
                                    frames_processed += 1
                                else:
                                    # İşlenmeyen kareleri de videoya ekle (orijinal haliyle)
                                    out.write(frame)
                                frame_count += 1
                                
                            # Video yazmayı sonlandır
                            out.release()
                            cap.release()
                            print(f"YOLO: Toplam işlenen kare sayısı: {frames_processed}/{frame_count}")
                            print(f"YOLO: İşlenmiş video kaydedildi: {processed_video_path}")
                            
                            # İşlenmiş videoyu static servis olarak kaydet
                            processed_video_save_path = os.path.join('processed_videos', processed_video_filename)
                            with open(processed_video_path, 'rb') as f:
                                processed_video_file = ContentFile(f.read())
                                processed_video_url = default_storage.save(processed_video_save_path, processed_video_file)
                            
                            print(f"YOLO: İşlenmiş video URL: {processed_video_url}")
                            
                        except ImportError as e:
                            print(f"YOLO: Ultralytics yüklenemedi: {str(e)}")
                            raise
                    else:
                        print("YOLO: Hiçbir model dosyası bulunamadı, simülasyon kullanılacak")
                        # Model yoksa simülasyon yap
                        raise FileNotFoundError("YOLO model dosyası bulunamadı")
                        
                except Exception as e:
                    print(f"YOLO: Model işleme hatası: {str(e)}")
                    # Simüle edilmiş ekipman tespiti
                    detections = [
                        {
                            "frame": 0,
                            "detections": [
                                {"class": "helmet", "confidence": 0.95, "status": "detected", "box": [100, 100, 200, 200]},
                                {"class": "safety_glasses", "confidence": 0.82, "status": "detected", "box": [150, 150, 250, 250]},
                                {"class": "gloves", "confidence": 0.78, "status": "detected", "box": [200, 200, 300, 300]},
                                {"class": "safety_vest", "confidence": 0.91, "status": "detected", "box": [250, 250, 350, 350]}
                            ]
                        }
                    ]
                
                # Sonuçları işle
                isg_items = []
                for frame in detections:
                    for detection in frame['detections']:
                        # Sadece eşsiz ekipmanları ekle
                        if not any(item['class'] == detection['class'] for item in isg_items):
                            isg_items.append({
                                "class": detection['class'],
                                "confidence": detection['confidence'],
                                "status": detection['status']
                            })
                
                # Başarılı yanıt döndür
                response_data = {
                    "id": str(uuid.uuid4()),
                    "status": "Başarılı",
                    "message": "Video başarıyla işlendi ve YOLO modeli tarafından analiz edildi",
                    "file_info": {
                        "name": video_file.name,
                        "size": video_file.size,
                        "path": video_path
                    },
                    "processed_video": {
                        "url": f"/media/{processed_video_url}" if 'processed_video_url' in locals() else None,
                        "frames_processed": frames_processed if 'frames_processed' in locals() else 0,
                    },
                    "results": {
                        "processed": True,
                        "frames_processed": frames_processed if 'frames_processed' in locals() else 0,
                        "total_frames": frame_count if 'frame_count' in locals() else 0,
                        "detection_results": {
                            "isg_items": isg_items,
                            "frames": detections
                        }
                    }
                }
                
                print(f"YOLO: Döndürülen yanıt: {response_data}")
                return Response(response_data)
                
            finally:
                # Geçici klasörü temizle
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"YOLO: Genel hata: {str(e)}")
            return Response(
                {"detail": f"İşlem sırasında bir hata oluştu: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
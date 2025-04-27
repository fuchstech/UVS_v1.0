"""
Hem kamera hem de yüklenen video için görüntü işleme modülü
"""
import cv2
import os
import time
import uuid
import numpy as np
import threading
import tempfile
from pathlib import Path
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@method_decorator(csrf_exempt, name='dispatch')
class CombinedProcessorView(APIView):
    """
    Hem kameradan hem de yüklenen videodan görüntü işleyen API
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def __init__(self):
        super().__init__()
        self.video_source = None  # Kamera veya video dosyası
        self.is_processing = False
        self.last_frame = None
        self.detections = []
        self.frame_count = 0
        self.model = None
        self.lock = threading.Lock()
        self.source_type = None  # 'camera' veya 'video'
        self.temp_dir = None
    
    def post(self, request, format=None):
        """Video yükleme ve kamera/video seçimi"""
        source_type = request.data.get('source_type', 'camera')
        
        if self.is_processing:
            # Mevcut işlem varsa durdur
            self._stop_processing()
        
        # Önceki verileri temizle
        self.frame_count = 0
        self.detections = []
        self.last_frame = None
        
        try:
            # YOLO modelini yükle
            if not self.model:
                self._load_model()
            
            self.source_type = source_type
            
            if source_type == 'camera':
                # Kamera indeksi
                camera_id = request.data.get('camera_id', '0')
                try:
                    camera_id = int(camera_id)
                except ValueError:
                    pass  # IP kamera URL'si olabilir
                
                print(f"Kamera {camera_id} açılıyor...")
                self.video_source = cv2.VideoCapture(camera_id)
                self.video_source.set(3, 1280)  # Genişlik
                self.video_source.set(4, 720)   # Yükseklik
                
                if not self.video_source.isOpened():
                    return Response({"error": f"Kamera açılamadı: {camera_id}"}, 
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            elif source_type == 'video':
                # Video dosyası
                video_file = request.FILES.get('video')
                if not video_file:
                    return Response({"error": "Video dosyası gerekli."}, 
                                    status=status.HTTP_400_BAD_REQUEST)
                
                # Geçici klasör oluştur
                self.temp_dir = tempfile.mkdtemp()
                temp_video_path = os.path.join(self.temp_dir, video_file.name)
                
                # Dosyayı geçici konuma kaydet
                with open(temp_video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                
                print(f"Video dosyası açılıyor: {temp_video_path}")
                self.video_source = cv2.VideoCapture(temp_video_path)
                
                if not self.video_source.isOpened():
                    return Response({"error": "Video dosyası açılamadı"}, 
                                    status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({"error": "Geçersiz kaynak tipi. 'camera' veya 'video' olmalı."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # İşlemeyi başlat
            self.is_processing = True
            processing_thread = threading.Thread(target=self._process_frames)
            processing_thread.daemon = True
            processing_thread.start()
            
            return Response({
                "status": "success",
                "message": f"{source_type.capitalize()} işleme başlatıldı",
                "stream_url": "/combined-stream/"  # MJPEG akışı için URL
            })
            
        except Exception as e:
            print(f"COMBINED hata: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Video akışını döndür"""
        if not self.is_processing or not self.video_source:
            return Response({"error": "İşlem henüz başlatılmadı"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # MJPEG olarak video akışı
        return StreamingHttpResponse(self._generate_frames(), 
                                    content_type='multipart/x-mixed-replace; boundary=frame')
    
    def delete(self, request):
        """İşlemeyi durdur"""
        self._stop_processing()
        return Response({"status": "İşlem durduruldu"})
    
    def _load_model(self):
        """YOLO modelini yükle"""
        try:
            import torch
            from ultralytics import YOLO
            
            # Mevcut dizini kontrol et
            base_dir = Path(__file__).resolve().parent.parent.parent
            yolo_path = base_dir / 'yolo_models'
            
            # Baret tespiti için model dosyasını bul
            model_paths = [
                yolo_path / 'hemletYoloV8_100epochs.pt',  # Baret modeli
                yolo_path / 'isg_model.pt',               # ISG modeli
                yolo_path / 'yolov8n.pt'                  # Varsayılan model
            ]
            
            # PyTorch 2.6 güvenlik ayarları
            try:
                import ultralytics.nn.tasks
                print("COMBINED: Torch güvenlik ayarları yapılıyor...")
                torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
            except (ImportError, AttributeError) as e:
                print(f"COMBINED: Torch güvenlik ayarı hatası: {str(e)}")
            
            # Model dosyasını bul ve yükle
            model_file = None
            for path in model_paths:
                if path.exists():
                    model_file = str(path)
                    print(f"COMBINED: Model bulundu: {path}")
                    break
            
            if model_file:
                try:
                    # Alternatif yöntemler
                    self.model = YOLO(model_file)
                    print(f"COMBINED: Model yüklendi: {model_file}")
                except Exception as e:
                    print(f"COMBINED: Model yükleme hatası: {str(e)}")
                    # Simülasyon modu
                    self.model = None
                    print("COMBINED: Simülasyon moduna geçiliyor")
                
                # Baret modeli sınıf isimleri
                self.class_names = ["head without helmet", "head with helmet"]
            else:
                print("COMBINED: Hiçbir model dosyası bulunamadı!")
                self.model = None
                
        except ImportError as e:
            print(f"COMBINED: YOLO modülü yüklenemedi - {str(e)}")
            self.model = None
    
    def _process_frames(self):
        """Kamera veya video karelerini işle"""
        fps = 30
        prev_time = time.time()
        
        # Video kaynak kontrolü
        if not self.video_source or not self.video_source.isOpened():
            print("COMBINED: Video kaynağı açık değil!")
            self.is_processing = False
            return
        
        # Video işleme
        while self.is_processing and self.video_source and self.video_source.isOpened():
            try:
                success, frame = self.video_source.read()
                if not success:
                    # Video dosyası bitmiş olabilir, tekrar başlat
                    if self.source_type == 'video':
                        print("COMBINED: Video sona erdi, başa dönülüyor")
                        self.video_source.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        print("COMBINED: Kamera karesi okunamadı!")
                        break
                
                # FPS hesaplama
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time
                
                # YOLO işleme
                detections = []
                if self.model:
                    try:
                        results = self.model.predict(source=frame, conf=0.5, verbose=False)
                        
                        for r in results:
                            boxes = r.boxes
                            for box in boxes:
                                # Bounding Box
                                x1, y1, x2, y2 = box.xyxy[0]
                                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                w, h = x2 - x1, y2 - y1
                                
                                # Confidence
                                conf = float(box.conf[0])
                                
                                # Class Name
                                cls = int(box.cls[0])
                                class_name = self.class_names[0] if cls >= len(self.class_names) else self.class_names[cls]
                                
                                # Sınıfa göre renk belirleme
                                color = (0, 255, 0) if "with helmet" in class_name else (0, 0, 255)
                                
                                # Kutu çizme
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                
                                # Sınıf adı ve güven değeri
                                label = f"{class_name} {conf:.2f}"
                                t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
                                cv2.rectangle(frame, (x1, y1-t_size[1]-10), (x1+t_size[0], y1), color, -1)
                                cv2.putText(frame, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                                
                                # Tespitleri kaydet
                                detections.append({
                                    'class': class_name,
                                    'confidence': round(conf, 2),
                                    'box': [int(x1), int(y1), int(x2), int(y2)]
                                })
                    except Exception as e:
                        print(f"COMBINED: Model işleme hatası: {str(e)}")
                
                # FPS ve kaynak türü göster
                fps_text = f"FPS: {int(fps)}"
                cv2.putText(frame, fps_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                source_text = f"Kaynak: {'Kamera' if self.source_type == 'camera' else 'Video'}"
                cv2.putText(frame, source_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Kare sayısı
                self.frame_count += 1
                cv2.putText(frame, f"Kare: {self.frame_count}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Thread-safe şekilde kareyi ve tespitleri güncelle
                with self.lock:
                    self.last_frame = frame.copy()
                    self.detections = detections
                
            except Exception as e:
                print(f"COMBINED: İşleme hatası: {str(e)}")
                time.sleep(0.1)
    
    def _generate_frames(self):
        """MJPEG akışı için kare üret"""
        while self.is_processing:
            try:
                with self.lock:
                    if self.last_frame is not None:
                        frame = self.last_frame.copy()
                    else:
                        time.sleep(0.1)
                        continue
                
                # JPEG dönüşümü
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # MJPEG formatında gönder
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Yayın hızını düzenle
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"COMBINED: Akış hatası: {str(e)}")
                time.sleep(0.1)
    
    def _stop_processing(self):
        """İşleme ve video kaynağını durdur"""
        self.is_processing = False
        
        if self.video_source:
            self.video_source.release()
            self.video_source = None
        
        # Geçici dosyaları temizle
        if self.temp_dir:
            import shutil
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.temp_dir = None
            except Exception as e:
                print(f"COMBINED: Geçici dosya temizleme hatası: {str(e)}")

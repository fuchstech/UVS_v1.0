"""
Canlı video akışı işleme modülü - kameradan görüntü alıp işler
"""
import cv2
import os
import time
import uuid
import numpy as np
import threading
import base64
from pathlib import Path
from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LivestreamProcessorView(APIView):
    """
    Kameradan canlı görüntü işleyen ve sonuçları sunan API
    """
    def __init__(self):
        super().__init__()
        self.video_camera = None
        self.is_processing = False
        self.last_frame = None
        self.detections = []
        self.frame_count = 0
        self.model = None
        self.lock = threading.Lock()
    
    def get(self, request):
        """Video akışını başlat"""
        # Kamera indeksi veya URL'den gelen stream
        camera_id = request.query_params.get('camera_id', '0')
        
        try:
            camera_id = int(camera_id)  # Webcam için sayısal indeks
        except ValueError:
            pass  # IP kamera URL'si olabilir
        
        try:
            print(f"Kamera {camera_id} açılıyor...")
            
            # YOLO modelini yükle
            try:
                from ultralytics import YOLO
                
                # Mevcut dizini kontrol et
                base_dir = Path(__file__).resolve().parent.parent.parent
                yolo_path = base_dir / 'yolo_models'
                
                # Modeli bul
                model_paths = [
                    yolo_path / 'hemletYoloV8_100epochs.pt',  # Verdiğiniz baret modeli
                    yolo_path / 'isg_model.pt',  # ISG modeli 
                    yolo_path / 'yolov8n.pt'     # Varsayılan model
                ]
                
                model_file = None
                for path in model_paths:
                    if path.exists():
                        model_file = str(path)
                        print(f"LIVESTREAM: Model bulundu: {path}")
                        break
                
                if model_file:
                    self.model = YOLO(model_file)
                    self.class_names = ["head without helmet","head with helmet"]  # Baret modeli sınıfları
                    print(f"LIVESTREAM: Model yüklendi: {model_file}")
                else:
                    print("LIVESTREAM: Hiçbir model dosyası bulunamadı!")
                    return Response({"error": "YOLO model dosyası bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
                    
            except ImportError as e:
                print(f"LIVESTREAM: YOLO modülü yüklenemedi - {str(e)}")
                return Response({"error": f"YOLO modülü yüklenemedi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Kamera akışını başlat
            self.video_camera = cv2.VideoCapture(camera_id)
            self.video_camera.set(3, 1280)  # Genişlik
            self.video_camera.set(4, 720)   # Yükseklik
            
            if not self.video_camera.isOpened():
                return Response({"error": f"Kamera açılamadı: {camera_id}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            self.is_processing = True
            
            # İşleme thread'ini başlat
            processing_thread = threading.Thread(target=self._process_frames)
            processing_thread.daemon = True
            processing_thread.start()
            
            # SSE (Server-Sent Events) yanıtı döndür
            return StreamingHttpResponse(self._generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
            
        except Exception as e:
            print(f"LIVESTREAM hata: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_frames(self):
        """Kamera karelerini YOLO ile işler"""
        fps = 30
        prev_time = time.time()
        
        while self.is_processing and self.video_camera and self.video_camera.isOpened():
            try:
                success, frame = self.video_camera.read()
                if not success:
                    print("LIVESTREAM: Kamera karesi okunamadı!")
                    break
                
                # FPS hesaplama
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time
                
                # YOLO işleme
                detections = []
                if self.model:
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
                            
                            # Kutu çizme
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0) if "with helmet" in class_name else (0, 0, 255), 2)
                            
                            # Sınıf adı ve güven değeri
                            label = f"{class_name} {conf:.2f}"
                            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                            cv2.rectangle(frame, (x1, y1-t_size[1]-15), (x1+t_size[0], y1), (0, 255, 0) if "with helmet" in class_name else (0, 0, 255), -1)
                            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                            
                            detections.append({
                                'class': class_name,
                                'confidence': round(conf, 2),
                                'box': [int(x1), int(y1), int(x2), int(y2)]
                            })
                
                # FPS göster
                cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Kare sayısı göster
                self.frame_count += 1
                cv2.putText(frame, f"Frame: {self.frame_count}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Güvenli şekilde son kareyi ve tespitleri güncelle
                with self.lock:
                    self.last_frame = frame.copy()
                    self.detections = detections
                
                # Daha akıcı bir deneyim için kısa bir bekleme
                # time.sleep(0.01)
                
            except Exception as e:
                print(f"LIVESTREAM işleme hatası: {str(e)}")
                time.sleep(0.1)  # Hata durumunda kısa bir bekleme
    
    def _generate_frames(self):
        """Kare akışını MJPEG formatında döndürür"""
        while self.is_processing:
            try:
                with self.lock:
                    if self.last_frame is not None:
                        frame = self.last_frame.copy()
                    else:
                        continue
                
                # JPEG'e dönüştür
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # MJPEG formatında streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Yayın hızını düzenlemek için
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"LIVESTREAM akış hatası: {str(e)}")
                time.sleep(0.1)
    
    def delete(self, request):
        """Video akışını durdur"""
        self.is_processing = False
        if self.video_camera:
            self.video_camera.release()
            self.video_camera = None
        return Response({"status": "Video akışı durduruldu"})

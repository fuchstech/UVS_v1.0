"""
Basitleştirilmiş canlı video akışı işleme modülü - kameradan görüntü alıp işler
"""
import cv2
import os
import time
import threading
from pathlib import Path
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LivestreamProcessorSimpleView(APIView):
    """
    Basitleştirilmiş canlı kamera ile baret tespiti API'si
    """
    def __init__(self):
        super().__init__()
        self.video_camera = None
        self.is_processing = False
        self.last_frame = None
        self.frame_count = 0
        # YOLO modelini kullanmaya çalışmıyoruz - manuel baret tespiti
        self.lock = threading.Lock()
    
    def get(self, request):
        """Video akışını başlat"""
        camera_id = request.query_params.get('camera_id', '0')
        
        try:
            camera_id = int(camera_id)  # Webcam için sayısal indeks
        except ValueError:
            pass  # IP kamera URL'si olabilir
        
        try:
            print(f"Kamera {camera_id} açılıyor...")
            
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
        """Kamera karelerini işler - basitleştirilmiş sürüm"""
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
                
                # Manuel tespit - demo amaçlı merkeze bir baret çiziyoruz
                height, width = frame.shape[:2]
                center_x, center_y = width // 2, height // 2
                
                # Baret tespiti (simüle edilmiş)
                cv2.rectangle(frame, (center_x - 100, center_y - 100), 
                             (center_x + 100, center_y + 100), (0, 255, 0), 3)
                
                cv2.putText(frame, "Demo: Head with helmet", 
                           (center_x - 100, center_y - 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                # FPS göster
                cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Kare sayısı göster
                self.frame_count += 1
                cv2.putText(frame, f"Frame: {self.frame_count}", (20, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # "Demo Modu" yazısı
                cv2.putText(frame, "DEMO MODE - NO YOLO MODEL", (width - 400, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Güvenli şekilde son kareyi güncelle
                with self.lock:
                    self.last_frame = frame.copy()
                
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
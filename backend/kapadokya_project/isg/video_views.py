import os
import tempfile
import cv2
import logging
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from kapadokya_project.api.models import Camera, ProcessedImage
from .tasks import process_image_task

logger = logging.getLogger(__name__)

class ProcessVideoAPIView(APIView):
    """
    API endpoint to process video uploads
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, format=None):
        try:
            logger.info("Video işleme isteği alındı")
            logger.debug(f"Gelen veri: {request.data}")
            
            # Get camera ID from request
            camera_id = request.data.get('camera_id')
            if not camera_id:
                logger.error("Kamera ID'si eksik")
                return Response(
                    {"detail": "Kamera ID'si gerekli."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                camera = Camera.objects.get(id=camera_id)
                logger.info(f"Kamera bulundu: {camera.name}")
            except Camera.DoesNotExist:
                logger.error(f"Kamera bulunamadı (ID: {camera_id})")
                return Response(
                    {"detail": "Kamera bulunamadı."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Handle video upload
            video_file = request.FILES.get('video')
            if not video_file:
                logger.error("Video dosyası yok")
                return Response(
                    {"detail": "Video dosyası gerekli."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Video dosyası alındı: {video_file.name}, boyut: {video_file.size} byte")
            
            # Geçici bir dosya yolu oluştur ve video dosyasını kaydet
            temp_dir = tempfile.mkdtemp()
            temp_video_path = os.path.join(temp_dir, video_file.name)
            logger.debug(f"Geçici dosya yolu: {temp_video_path}")
            
            with open(temp_video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            
            logger.info(f"Video geçici konuma kaydedildi: {temp_video_path}")
            
            # Video'yu kare kare işleme
            processed_images = []
            results = []
            sample_rate = int(request.data.get('sample_rate', 30))  # Her 30 karede bir işlem yap (default)
            
            try:
                cap = cv2.VideoCapture(temp_video_path)
                
                if not cap.isOpened():
                    logger.error(f"Video dosyası açılamadı: {temp_video_path}")
                    return Response(
                        {"detail": "Video dosyası açılamadı. Dosya formatı desteklenmiyor olabilir."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                frame_count = 0
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                logger.info(f"Video özellikleri: Toplam kare: {total_frames}, FPS: {fps}, Örnekleme hızı: {sample_rate}")
                
                while cap.isOpened() and frame_count < total_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    if frame_count % sample_rate == 0:  # Sadece belirli aralıklarla kare işle
                        # Kareyi resim olarak kaydet
                        frame_file_name = f"frame_{frame_count}.jpg"
                        frame_file_path = os.path.join(temp_dir, frame_file_name)
                        cv2.imwrite(frame_file_path, frame)
                        
                        # Dosyayı ProcessedImage modeline kaydet
                        with open(frame_file_path, 'rb') as f:
                            image_content = f.read()
                            
                        frame_path = default_storage.save(f'uploads/{frame_file_name}', ContentFile(image_content))
                        logger.debug(f"Kare kaydedildi: {frame_path}")
                        
                        processed_image = ProcessedImage.objects.create(
                            camera=camera,
                            original_image=frame_path,
                            detection_results={},  # Boş sonuçlar, task tarafından güncellenecek
                        )
                        
                        # Resim işleme görevini başlat
                        process_image_task.delay(processed_image.id)
                        
                        processed_images.append(processed_image.id)
                        results.append({
                            "frame": frame_count,
                            "processed_image_id": processed_image.id,
                            "status": "Kare işleme kuyruğa alındı"
                        })
                        
                    frame_count += 1
                    
                cap.release()
                logger.info(f"Video işleme tamamlandı. İşlenen kare sayısı: {len(processed_images)}")
                
            except Exception as e:
                logger.exception(f"Video işleme hatası: {str(e)}")
                return Response(
                    {"detail": f"Video işleme hatası: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            finally:
                # Geçici dosyaları temizle
                import shutil
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.debug(f"Geçici dosyalar temizlendi: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Geçici dosyalar temizlenirken hata: {str(e)}")
            
            return Response({
                "processed_frames": len(processed_images),
                "total_frames": frame_count,
                "processed_image_ids": processed_images,
                "results": results,
                "status": "Video işleme tamamlandı",
                "message": "Kareler işleniyor, sonuçlar yakında hazır olacak."
            })
            
        except Exception as e:
            logger.exception(f"Genel hata: {str(e)}")
            return Response(
                {"detail": f"İşlem sırasında bir hata oluştu: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
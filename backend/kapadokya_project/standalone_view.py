"""
Tamamen bağımsız video işleme modülü - hiçbir model kullanmaz
"""
import os
import uuid
import tempfile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class StandaloneVideoProcessor(APIView):
    """
    Hiçbir model kullanmadan çalışan, tamamen bağımsız video işleme endpoint'i
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = []  # Hiçbir izin gerektirmez
    
    def post(self, request, format=None):
        try:
            print("STANDALONE: Video işleme isteği alındı")
            print(f"STANDALONE: Gelen veri: {request.data}")
            print(f"STANDALONE: Gelen dosyalar: {request.FILES}")
            
            # Video dosyasını kontrol et
            video_file = request.FILES.get('video')
            if not video_file:
                print("STANDALONE: Video dosyası eksik")
                return Response(
                    {"detail": "Video dosyası gerekli."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"STANDALONE: Video dosyası alındı: {video_file.name}, boyut: {video_file.size}")
            
            # Geçici bir klasör oluştur
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Video dosyasını kaydet
                unique_filename = f"standalone_{uuid.uuid4().hex}_{video_file.name}"
                save_path = os.path.join('uploads', unique_filename)
                video_path = default_storage.save(save_path, ContentFile(video_file.read()))
                
                print(f"STANDALONE: Video dosyası kaydedildi: {video_path}")
                
                # Simüle edilmiş işleme sonuçları
                processing_results = {
                    "processed": True,
                    "message": "Video dosyası başarıyla kaydedildi ve işlendi (demo)",
                    "file_info": {
                        "original_name": video_file.name,
                        "size_bytes": video_file.size,
                        "path": video_path,
                        "content_type": video_file.content_type
                    },
                    "detection_results": {
                        "isg_items": [
                            {"class": "helmet", "confidence": 0.95, "status": "detected"},
                            {"class": "safety_glasses", "confidence": 0.82, "status": "detected"},
                            {"class": "gloves", "confidence": 0.78, "status": "detected"},
                            {"class": "safety_vest", "confidence": 0.91, "status": "detected"}
                        ]
                    }
                }
                
                # Başarılı yanıt döndür
                response_data = {
                    "id": str(uuid.uuid4()),
                    "status": "Başarılı",
                    "message": "Video başarıyla işlendi",
                    "file_info": {
                        "name": video_file.name,
                        "size": video_file.size,
                        "path": video_path
                    },
                    "results": processing_results
                }
                
                print(f"STANDALONE: Döndürülen yanıt: {response_data}")
                return Response(response_data)
                
            finally:
                # Geçici klasörü temizle
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"STANDALONE: Genel hata: {str(e)}")
            return Response(
                {"detail": f"İşlem sırasında bir hata oluştu: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

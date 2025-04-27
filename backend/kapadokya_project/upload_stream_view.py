"""
Streaming için video yükleme modülü
"""
import os
import uuid
import tempfile
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

class UploadStreamVideoView(APIView):
    """
    Streaming için video yükleme API'si
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            print("UPLOAD STREAM: Video yükleme isteği alındı")
            
            # Video dosyasını kontrol et
            video_file = request.FILES.get('video')
            if not video_file:
                print("UPLOAD STREAM: Video dosyası eksik")
                return Response(
                    {"detail": "Video dosyası gerekli."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"UPLOAD STREAM: Video dosyası alındı: {video_file.name}, boyut: {video_file.size}")
            
            # Stream modu kontrolü
            stream_mode = request.data.get('stream_mode', 'false')
            is_stream_mode = stream_mode.lower() == 'true'
            
            # Benzersiz dosya adı oluştur
            unique_filename = f"stream_{uuid.uuid4().hex}_{video_file.name}"
            
            # Stream işlemi için uploads klasörü (livestream_processor.py ile aynı klasör)
            save_path = os.path.join('uploads', unique_filename)
            
            # Video dosyasını kaydet
            video_path = default_storage.save(save_path, ContentFile(video_file.read()))
            
            print(f"UPLOAD STREAM: Video dosyası stream için kaydedildi: {video_path}")
            # Tam dosya yolunu göster
            print(f"UPLOAD STREAM: Tam dosya yolu: {default_storage.path(video_path)}")
            
            # Başarılı yanıt
            return Response({
                "status": "success",
                "message": "Video başarıyla yüklendi ve stream için hazır",
                "video_id": unique_filename,
                "video_path": video_path,
                "stream_mode": is_stream_mode
            })
            
        except Exception as e:
            print(f"UPLOAD STREAM: Hata: {str(e)}")
            return Response(
                {"detail": f"Video yükleme hatası: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

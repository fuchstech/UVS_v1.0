from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

class SimpleVideoUploadView(APIView):
    """
    Çok basit video yükleme endpoint'i - 
    Hiçbir kimlik doğrulama veya izin gerektirmez
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = []  # Boş liste tüm izinleri devre dışı bırakır
    
    def post(self, request, format=None):
        """Basit bir video yükleme testi"""
        print("Basit video yükleme isteği alındı!")
        
        if 'video' not in request.FILES:
            return Response(
                {"error": "Video dosyası gerekli"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        video_file = request.FILES['video']
        
        # Dosya bilgilerini çıktıla
        file_info = {
            "dosya_adı": video_file.name,
            "boyut_bytes": video_file.size,
            "content_type": video_file.content_type
        }
        
        print(f"Dosya bilgisi: {file_info}")
        
        # Başarılı yanıt döndür
        return Response({
            "message": "Video başarıyla alındı",
            "file_info": file_info,
            "success": True
        })
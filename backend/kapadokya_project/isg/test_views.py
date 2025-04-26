from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

class VideoUploadTestView(APIView):
    """
    Basit video yükleme testi için endpoint
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # Herhangi bir kimlik doğrulama gerektirme
    
    def post(self, request, format=None):
        """
        Video dosyasını alıp basit bir yanıt döndürür - video işlemeden
        """
        # Get the video file
        video_file = request.FILES.get('video')
        if not video_file:
            return Response(
                {"detail": "Video dosyası gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get camera ID
        camera_id = request.data.get('camera_id')
        if not camera_id:
            return Response(
                {"detail": "Kamera ID'si gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log info about the file
        file_info = {
            "filename": video_file.name,
            "size": video_file.size,
            "content_type": video_file.content_type
        }
        
        # Return success with file info
        return Response({
            "success": True,
            "message": "Video dosyası başarıyla alındı (İşleme yapılmadı)",
            "file_info": file_info,
            "camera_id": camera_id
        })

from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import Camera, Zone, ProcessedImage
from .serializers import UserSerializer, CameraSerializer, ZoneSerializer, ProcessedImageSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view users
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CameraViewSet(viewsets.ModelViewSet):
    """
    API endpoint for camera management
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Camera.objects.all()
        camera_type = self.request.query_params.get('type', None)
        if camera_type is not None:
            queryset = queryset.filter(camera_type=camera_type)
        return queryset

class ZoneViewSet(viewsets.ModelViewSet):
    """
    API endpoint for zone management
    """
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Zone.objects.all()
        camera_id = self.request.query_params.get('camera', None)
        is_danger = self.request.query_params.get('is_danger', None)
        
        if camera_id is not None:
            queryset = queryset.filter(camera_id=camera_id)
            
        if is_danger is not None:
            is_danger_bool = is_danger.lower() == 'true'
            queryset = queryset.filter(is_danger_zone=is_danger_bool)
            
        return queryset

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Camera, Zone, ProcessedImage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'

class CameraSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = Camera
        fields = '__all__'
        
class ProcessedImageSerializer(serializers.ModelSerializer):
    camera_name = serializers.ReadOnlyField(source='camera.name')
    
    class Meta:
        model = ProcessedImage
        fields = '__all__'

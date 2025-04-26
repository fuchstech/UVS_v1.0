from django.db import models
from django.contrib.auth.models import User

class Camera(models.Model):
    """Camera model for video streams or image inputs"""
    name = models.CharField(max_length=100)
    stream_url = models.URLField(blank=True, null=True)  # For IP cameras
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=200)
    camera_type = models.CharField(max_length=50, choices=(
        ('isg', 'İş Sağlığı ve Güvenliği'),
        ('verim', 'Verimlilik İzleme'),
        ('urun', 'Ürün Kalite Kontrol'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_camera_type_display()}"

class Zone(models.Model):
    """Zones in the work area for safety monitoring"""
    name = models.CharField(max_length=100)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='zones')
    is_danger_zone = models.BooleanField(default=False)
    coordinates = models.JSONField(help_text="Polygon coordinates defining the zone")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        zone_type = "Tehlikeli Alan" if self.is_danger_zone else "Normal Alan"
        return f"{self.name} - {zone_type}"

class ProcessedImage(models.Model):
    """Stores processed images with detection results"""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='processed_images')
    original_image = models.ImageField(upload_to='uploads/')
    processed_image = models.ImageField(upload_to='processed/')
    detection_results = models.JSONField()  # JSON of detection results
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Processed Image {self.id} - {self.camera.name} - {self.timestamp}"

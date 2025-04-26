from django.db import models
from django.contrib.auth.models import User
from kapadokya_project.api.models import Camera, Zone, ProcessedImage

class SafetyEquipment(models.Model):
    """Safety equipment types that need to be detected"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    detection_class = models.CharField(max_length=50, help_text="YOLOv11 class name for detection")
    
    def __str__(self):
        return self.name

class SafetyViolation(models.Model):
    """Record of safety violations detected by AI"""
    processed_image = models.ForeignKey(ProcessedImage, on_delete=models.CASCADE, related_name='safety_violations')
    violation_type = models.CharField(max_length=100, choices=(
        ('missing_equipment', 'Eksik Güvenlik Ekipmanı'),
        ('danger_zone', 'Tehlikeli Alan İhlali'),
        ('unauthorized_entry', 'Yetkisiz Giriş'),
    ))
    equipment = models.ForeignKey(SafetyEquipment, on_delete=models.SET_NULL, null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_violation_type_display()} - {self.timestamp}"

class SafetyReport(models.Model):
    """Aggregated safety reports"""
    report_date = models.DateField()
    total_violations = models.IntegerField(default=0)
    resolved_violations = models.IntegerField(default=0)
    missing_equipment_count = models.IntegerField(default=0)
    danger_zone_count = models.IntegerField(default=0)
    unauthorized_entry_count = models.IntegerField(default=0)
    report_data = models.JSONField(null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Güvenlik Raporu - {self.report_date}"

    class Meta:
        ordering = ['-report_date']

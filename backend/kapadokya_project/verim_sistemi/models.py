from django.db import models
from django.contrib.auth.models import User
from kapadokya_project.api.models import Camera, ProcessedImage

class Worker(models.Model):
    """Worker model for productivity tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"

class WorkArea(models.Model):
    """Work areas for productivity tracking"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cameras = models.ManyToManyField(Camera, related_name='work_areas')
    
    def __str__(self):
        return self.name

class ProductivityMetric(models.Model):
    """Metrics for measuring worker productivity"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    unit = models.CharField(max_length=50)
    target_value = models.FloatField()
    
    def __str__(self):
        return f"{self.name} ({self.unit})"

class WorkerActivity(models.Model):
    """Worker activity detected by AI"""
    processed_image = models.ForeignKey(ProcessedImage, on_delete=models.CASCADE, related_name='worker_activities')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    work_area = models.ForeignKey(WorkArea, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=(
        ('working', 'Çalışıyor'),
        ('idle', 'Boşta'),
        ('absent', 'Yerinde Yok'),
        ('break', 'Mola'),
        ('unknown', 'Bilinmiyor'),
    ))
    detected_tools = models.JSONField(null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    
    def __str__(self):
        worker_name = self.worker.name if self.worker else "Bilinmeyen İşçi"
        return f"{worker_name} - {self.get_activity_type_display()} - {self.timestamp}"

class ProductivityData(models.Model):
    """Aggregated productivity data"""
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='productivity_data')
    work_area = models.ForeignKey(WorkArea, on_delete=models.CASCADE)
    date = models.DateField()
    working_time = models.PositiveIntegerField(default=0, help_text="Total working time in seconds")
    idle_time = models.PositiveIntegerField(default=0, help_text="Total idle time in seconds")
    absent_time = models.PositiveIntegerField(default=0, help_text="Total time not present in seconds")
    break_time = models.PositiveIntegerField(default=0, help_text="Total break time in seconds")
    productivity_score = models.FloatField(default=0.0)
    details = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.worker.name} - {self.date} - Score: {self.productivity_score:.2f}"
    
    class Meta:
        unique_together = ('worker', 'work_area', 'date')
        ordering = ['-date']

class Product(models.Model):
    """Product model for production tracking"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    detection_class = models.CharField(max_length=50, help_text="YOLOv11 class name for detection")
    expected_quality_features = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class ProductionCount(models.Model):
    """Production count detected by AI"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_counts')
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    defect_count = models.PositiveIntegerField(default=0)
    date = models.DateField()
    details = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.date} - Count: {self.count}"
    
    class Meta:
        unique_together = ('product', 'camera', 'date')
        ordering = ['-date']

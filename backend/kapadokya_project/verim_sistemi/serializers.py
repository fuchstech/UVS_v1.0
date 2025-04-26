from rest_framework import serializers
from .models import (
    Worker, WorkArea, ProductivityMetric, WorkerActivity, 
    ProductivityData, Product, ProductionCount
)

class WorkerSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username', default=None)
    
    class Meta:
        model = Worker
        fields = '__all__'

class WorkAreaSerializer(serializers.ModelSerializer):
    camera_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkArea
        fields = '__all__'
    
    def get_camera_count(self, obj):
        return obj.cameras.count()

class ProductivityMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivityMetric
        fields = '__all__'

class WorkerActivitySerializer(serializers.ModelSerializer):
    worker_name = serializers.ReadOnlyField(source='worker.name', default="Bilinmeyen İşçi")
    work_area_name = serializers.ReadOnlyField(source='work_area.name')
    activity_type_display = serializers.ReadOnlyField(source='get_activity_type_display')
    
    class Meta:
        model = WorkerActivity
        fields = '__all__'

class ProductivityDataSerializer(serializers.ModelSerializer):
    worker_name = serializers.ReadOnlyField(source='worker.name')
    work_area_name = serializers.ReadOnlyField(source='work_area.name')
    
    class Meta:
        model = ProductivityData
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductionCountSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    camera_name = serializers.ReadOnlyField(source='camera.name')
    
    class Meta:
        model = ProductionCount
        fields = '__all__'

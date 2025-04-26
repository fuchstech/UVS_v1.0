from rest_framework import serializers
from .models import SafetyEquipment, SafetyViolation, SafetyReport

class SafetyEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyEquipment
        fields = '__all__'

class SafetyViolationSerializer(serializers.ModelSerializer):
    equipment_name = serializers.ReadOnlyField(source='equipment.name', default=None)
    zone_name = serializers.ReadOnlyField(source='zone.name', default=None)
    resolved_by_username = serializers.ReadOnlyField(source='resolved_by.username', default=None)
    
    class Meta:
        model = SafetyViolation
        fields = '__all__'

class SafetyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyReport
        fields = '__all__'

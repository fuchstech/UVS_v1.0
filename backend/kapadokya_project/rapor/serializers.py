from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Report, ReportTemplate, ScheduledReport, AIAnalysis, Dashboard

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    report_type_display = serializers.ReadOnlyField(source='get_report_type_display')
    
    class Meta:
        model = Report
        fields = '__all__'

class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    report_type_display = serializers.ReadOnlyField(source='get_report_type_display')
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'

class ScheduledReportSerializer(serializers.ModelSerializer):
    template_name = serializers.ReadOnlyField(source='template.name')
    frequency_display = serializers.ReadOnlyField(source='get_frequency_display')
    recipients = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = '__all__'

class AIAnalysisSerializer(serializers.ModelSerializer):
    report_title = serializers.ReadOnlyField(source='report.title')
    analysis_type_display = serializers.ReadOnlyField(source='get_analysis_type_display')
    priority_display = serializers.ReadOnlyField(source='get_priority_display')
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.get_full_name', default=None)
    
    class Meta:
        model = AIAnalysis
        fields = '__all__'

class DashboardSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    
    class Meta:
        model = Dashboard
        fields = '__all__'

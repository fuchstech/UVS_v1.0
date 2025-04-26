import os
import tempfile
import cv2
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import SafetyEquipment, SafetyViolation, SafetyReport
from .serializers import SafetyEquipmentSerializer, SafetyViolationSerializer, SafetyReportSerializer
from .tasks import process_image_task, generate_daily_safety_report
from kapadokya_project.api.models import Camera, ProcessedImage

class SafetyEquipmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for safety equipment management
    """
    queryset = SafetyEquipment.objects.all()
    serializer_class = SafetyEquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class SafetyViolationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for safety violations
    """
    queryset = SafetyViolation.objects.all().order_by('-timestamp')
    serializer_class = SafetyViolationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SafetyViolation.objects.all().order_by('-timestamp')
        
        # Filter by violation type
        violation_type = self.request.query_params.get('type', None)
        if violation_type:
            queryset = queryset.filter(violation_type=violation_type)
            
        # Filter by resolution status
        resolved = self.request.query_params.get('resolved', None)
        if resolved is not None:
            resolved_bool = resolved.lower() == 'true'
            queryset = queryset.filter(resolved=resolved_bool)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(timestamp__date__range=[start_date, end_date])
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def resolve_violation(self, request, pk=None):
        """Mark a violation as resolved"""
        violation = self.get_object()
        if violation.resolved:
            return Response(
                {"detail": "Bu ihlal zaten çözülmüş."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        violation.resolved = True
        violation.resolved_by = request.user
        violation.resolved_at = timezone.now()
        violation.resolution_notes = request.data.get('notes', '')
        violation.save()
        
        serializer = self.get_serializer(violation)
        return Response(serializer.data)

class SafetyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for safety reports
    """
    queryset = SafetyReport.objects.all()
    serializer_class = SafetyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Manually trigger report generation"""
        date_str = request.data.get('date', None)
        
        if date_str:
            # Schedule the task to generate report for specific date
            task = generate_daily_safety_report.delay(date_str)
            return Response({"task_id": task.id, "status": "Rapor oluşturma işlemi başlatıldı"})
        else:
            return Response(
                {"detail": "Rapor için tarih gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProcessImageAPIView(APIView):
    """
    API endpoint to process images from cameras
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        # Get camera ID from request
        camera_id = request.data.get('camera_id')
        if not camera_id:
            return Response(
                {"detail": "Kamera ID'si gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            return Response(
                {"detail": "Kamera bulunamadı."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Handle image upload
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "Görüntü dosyası gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the original image
        processed_image = ProcessedImage.objects.create(
            camera=camera,
            original_image=image_file,
            detection_results={},  # Empty results, will be updated by task
        )
        
        # Process image in background
        process_image_task.delay(processed_image.id)
        
        return Response({
            "id": processed_image.id,
            "status": "Görüntü işleme kuyruğa alındı.",
            "message": "Görüntü işleniyor, sonuçlar yakında hazır olacak."
        })

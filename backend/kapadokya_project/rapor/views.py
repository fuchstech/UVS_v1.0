from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q

from .models import Report, ReportTemplate, ScheduledReport, AIAnalysis, Dashboard
from .serializers import (
    ReportSerializer, ReportTemplateSerializer, ScheduledReportSerializer,
    AIAnalysisSerializer, DashboardSerializer
)
from .tasks import generate_report, generate_ai_analysis

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reports
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Report.objects.all()
        
        # Filter by report type
        report_type = self.request.query_params.get('type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(
                Q(start_date__gte=start_date) | Q(end_date__lte=end_date)
            )
            
        # Filter by creator
        created_by = self.request.query_params.get('created_by', None)
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
            
        # Filter archived reports
        show_archived = self.request.query_params.get('archived', None)
        if show_archived is None or show_archived.lower() != 'true':
            queryset = queryset.filter(is_archived=False)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a report"""
        report = self.get_object()
        report.is_archived = True
        report.save()
        return Response({'status': 'report archived'})
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a report"""
        report = self.get_object()
        report.is_archived = False
        report.save()
        return Response({'status': 'report unarchived'})
    
    @action(detail=True, methods=['post'])
    def generate_ai_analysis(self, request, pk=None):
        """Generate AI analysis for a report"""
        report = self.get_object()
        task = generate_ai_analysis.delay(report.id)
        return Response({
            'task_id': task.id,
            'status': 'AI analiz oluşturma işlemi başlatıldı'
        })

class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for report templates
    """
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ReportTemplate.objects.all()
        
        # Filter by report type
        report_type = self.request.query_params.get('type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
            
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_report(self, request, pk=None):
        """Generate a report using this template"""
        template = self.get_object()
        
        # Get date range from request or use default
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)
        
        if not start_date or not end_date:
            return Response(
                {"detail": "Başlangıç ve bitiş tarihleri gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start the report generation task
        task = generate_report.delay(template.id, start_date, end_date, request.user.id)
        
        return Response({
            'task_id': task.id,
            'status': 'Rapor oluşturma işlemi başlatıldı',
            'message': 'Rapor arka planda oluşturuluyor, tamamlandığında erişilebilir olacak.'
        })

class ScheduledReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for scheduled reports
    """
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ScheduledReport.objects.all()
        
        # Filter by template
        template_id = self.request.query_params.get('template', None)
        if template_id:
            queryset = queryset.filter(template_id=template_id)
            
        # Filter by frequency
        frequency = self.request.query_params.get('frequency', None)
        if frequency:
            queryset = queryset.filter(frequency=frequency)
            
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a scheduled report"""
        scheduled_report = self.get_object()
        scheduled_report.is_active = not scheduled_report.is_active
        scheduled_report.save()
        return Response({
            'status': f"Scheduled report {'activated' if scheduled_report.is_active else 'deactivated'}"
        })

class AIAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for AI analyses
    """
    queryset = AIAnalysis.objects.all()
    serializer_class = AIAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AIAnalysis.objects.all()
        
        # Filter by report
        report_id = self.request.query_params.get('report', None)
        if report_id:
            queryset = queryset.filter(report_id=report_id)
            
        # Filter by analysis type
        analysis_type = self.request.query_params.get('type', None)
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
            
        # Filter by priority
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)
            
        # Filter by review status
        is_reviewed = self.request.query_params.get('reviewed', None)
        if is_reviewed is not None:
            is_reviewed_bool = is_reviewed.lower() == 'true'
            queryset = queryset.filter(is_reviewed=is_reviewed_bool)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Mark an AI analysis as reviewed"""
        analysis = self.get_object()
        analysis.is_reviewed = True
        analysis.reviewed_by = request.user
        analysis.review_notes = request.data.get('notes', '')
        analysis.save()
        return Response({'status': 'analysis marked as reviewed'})

class DashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user dashboards
    """
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own dashboards
        return Dashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically assign dashboard to current user
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this dashboard as the user's default"""
        dashboard = self.get_object()
        
        # Clear default flag on all other dashboards
        Dashboard.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this dashboard as default
        dashboard.is_default = True
        dashboard.save()
        
        return Response({'status': 'default dashboard updated'})
    
    @action(detail=False, methods=['get'])
    def get_default(self, request):
        """Get the user's default dashboard"""
        try:
            dashboard = Dashboard.objects.get(user=request.user, is_default=True)
            serializer = self.get_serializer(dashboard)
            return Response(serializer.data)
        except Dashboard.DoesNotExist:
            return Response(
                {"detail": "Varsayılan gösterge paneli bulunamadı."},
                status=status.HTTP_404_NOT_FOUND
            )

class GenerateReportView(APIView):
    """
    API endpoint to generate a custom report
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        config = request.data.get('config', {})
        
        if not report_type or not start_date or not end_date:
            return Response(
                {"detail": "Rapor tipi, başlangıç ve bitiş tarihleri gerekli."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a temporary template with the configuration
        template = ReportTemplate.objects.create(
            name=f"Geçici Şablon - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            report_type=report_type,
            config=config,
            created_by=request.user,
            is_active=False  # Temporary template
        )
        
        # Start the report generation task
        task = generate_report.delay(template.id, start_date, end_date, request.user.id)
        
        return Response({
            'task_id': task.id,
            'template_id': template.id,
            'status': 'Rapor oluşturma işlemi başlatıldı'
        })

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportViewSet, ReportTemplateViewSet, ScheduledReportViewSet,
    AIAnalysisViewSet, DashboardViewSet, GenerateReportView
)

router = DefaultRouter()
router.register(r'reports', ReportViewSet)
router.register(r'templates', ReportTemplateViewSet)
router.register(r'scheduled', ScheduledReportViewSet)
router.register(r'ai-analysis', AIAnalysisViewSet)
router.register(r'dashboards', DashboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-custom/', GenerateReportView.as_view(), name='generate-custom-report'),
]

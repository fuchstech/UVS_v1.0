from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SafetyEquipmentViewSet, SafetyViolationViewSet, SafetyReportViewSet, ProcessImageAPIView, HeatMapViewSet, PersonTrackingDataViewSet
from .video_views import ProcessVideoAPIView
from .test_views import VideoUploadTestView
from .simplified_video_view import SimplifiedVideoProcessorView

router = DefaultRouter()
router.register(r'equipment', SafetyEquipmentViewSet)
router.register(r'violations', SafetyViolationViewSet)
router.register(r'reports', SafetyReportViewSet)
router.register(r'heatmaps', HeatMapViewSet)
router.register(r'tracking-data', PersonTrackingDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process-image/', ProcessImageAPIView.as_view(), name='process-image'),
    path('process-video/', ProcessVideoAPIView.as_view(), name='process-video'),
    path('simple-process-video/', SimplifiedVideoProcessorView.as_view(), name='simple-process-video'),
    path('test-upload/', VideoUploadTestView.as_view(), name='test-upload'),  # Test endpoint
    path('resolve-violation/<int:pk>/', SafetyViolationViewSet.as_view({'post': 'resolve_violation'}), name='resolve-violation'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SafetyEquipmentViewSet, SafetyViolationViewSet, SafetyReportViewSet, ProcessImageAPIView

router = DefaultRouter()
router.register(r'equipment', SafetyEquipmentViewSet)
router.register(r'violations', SafetyViolationViewSet)
router.register(r'reports', SafetyReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process-image/', ProcessImageAPIView.as_view(), name='process-image'),
    path('resolve-violation/<int:pk>/', SafetyViolationViewSet.as_view({'post': 'resolve_violation'}), name='resolve-violation'),
]

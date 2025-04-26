from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkerViewSet, WorkAreaViewSet, ProductivityMetricViewSet,
    WorkerActivityViewSet, ProductivityDataViewSet, 
    ProductViewSet, ProductionCountViewSet,
    ProcessProductivityAPIView, ProcessProductCountAPIView
)

router = DefaultRouter()
router.register(r'workers', WorkerViewSet)
router.register(r'work-areas', WorkAreaViewSet)
router.register(r'metrics', ProductivityMetricViewSet)
router.register(r'activities', WorkerActivityViewSet)
router.register(r'productivity', ProductivityDataViewSet)
router.register(r'products', ProductViewSet)
router.register(r'production-counts', ProductionCountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process-productivity/', ProcessProductivityAPIView.as_view(), name='process-productivity'),
    path('process-product-count/', ProcessProductCountAPIView.as_view(), name='process-product-count'),
]

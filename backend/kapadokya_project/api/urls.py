from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CameraViewSet, ZoneViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'cameras', CameraViewSet)
router.register(r'zones', ZoneViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

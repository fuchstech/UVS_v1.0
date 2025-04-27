from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView
from .views import index, swagger_ui_view, static_swagger_view, static_redoc_view
from .test_upload_view import SimpleVideoUploadView
from .standalone_view import StandaloneVideoProcessor
from .yolo_processor import YoloVideoProcessor
from .livestream_processor import LivestreamProcessorView
from .livestream_processor_simple import LivestreamProcessorSimpleView

# Basitleştirilmiş Swagger şeması
schema_view = get_schema_view(
   openapi.Info(
      title="Kapadokya ÜVS API",
      default_version='v1',
      description="Kapadokya Üretim Verimlilik Sistemi API",
   ),
   public=True,
)

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    
    # Basit test endpoint'i
    path('test-upload/', SimpleVideoUploadView.as_view(), name='simple-test-upload'),
    path('standalone-video/', StandaloneVideoProcessor.as_view(), name='standalone-video-processor'),
    path('yolo-video/', YoloVideoProcessor.as_view(), name='yolo-video-processor'),
    path('livestream/', LivestreamProcessorView.as_view(), name='livestream-processor'),
    path('livestream-simple/', LivestreamProcessorSimpleView.as_view(), name='livestream-simple'),
    
    # API documentation
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', static_swagger_view, name='schema-swagger-ui'),
    path('redoc/', static_redoc_view, name='schema-redoc'),
    
    # API Dokümantasyon şeması
    path('api/api-schema.json', lambda request: HttpResponse(
        open('C:\\Users\\fuchs\\Desktop\\UVS_V1.0\\backend\\static\\api\\api-schema.json').read(),
        content_type='application/json'
    )),
    path('api/', include('kapadokya_project.api.urls')),
    path('api/isg/', include('kapadokya_project.isg.urls')),
    path('api/verim/', include('kapadokya_project.verim_sistemi.urls')),
    path('api/rapor/', include('kapadokya_project.rapor.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

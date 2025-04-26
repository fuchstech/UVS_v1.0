from django.shortcuts import render
from drf_yasg.views import get_schema_view
from django.conf import settings

def index(request):
    return render(request, 'welcome.html')

def swagger_ui_view(request):
    return render(request, 'swagger/swagger-ui.html', {
        'api_key': settings.API_KEY
    })

def static_swagger_view(request):
    return render(request, 'swagger-static.html')

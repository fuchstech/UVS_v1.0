from django.http import JsonResponse
from django.conf import settings
from django.urls import resolve

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # API endpointlerine yapılan istekleri denetle
        if request.path.startswith('/api/'):
            api_key_header = request.META.get('HTTP_X_API_KEY', '')
            if api_key_header != settings.API_KEY:
                return JsonResponse({'detail': 'Invalid or missing API key'}, status=403)
        
        # Swagger ve Admin endpointlerini istisnalardan say
        if request.path.startswith('/swagger/') or request.path.startswith('/admin/') or request.path == '/':
            return self.get_response(request)
        
        # Diğer istekleri işle
        response = self.get_response(request)
        return response

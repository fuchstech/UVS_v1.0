from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CameraViewSet(viewsets.ModelViewSet):
    # Placeholder for Camera model
    queryset = User.objects.none()
    serializer_class = UserSerializer

class ZoneViewSet(viewsets.ModelViewSet):
    # Placeholder for Zone model
    queryset = User.objects.none()
    serializer_class = UserSerializer

class LoginView(APIView):
    permission_classes = []  # No permission required

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'id': user.id,
                'username': user.username,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'role': 'Yönetici' if user.is_staff else 'Kullanıcı'
            })
        else:
            return Response(
                {'detail': 'Geçersiz kullanıcı adı veya şifre.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from profile_app.models import CustomerProfile, BusinessProfile
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        username = data["username"]
        email = data["email"]
        password = data["password"]
        user_type = data["type"]

        # User erstellen
        user = User.objects.create_user(username=username, email=email, password=password)

        # Profil anlegen
        if user_type == "customer":
            CustomerProfile.objects.create(user=user, type="customer")
        else:
            BusinessProfile.objects.create(user=user, type="business")

        # Token generieren
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Benutzername und Passwort erforderlich'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Ungültige Anmeldedaten'}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from profile_app.models import CustomerProfile, BusinessProfile
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    """
    API endpoint for registering a new user. Creates a Django User, associated profile,
    and authentication token.
    """
    def post(self, request):
        """
        Handle user registration.

        Expects 'username', 'email', 'password', and 'type' in request.data.
        Blocks reserved usernames, creates user and profile, and returns an auth token.
        """
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        username = data["username"]
        email = data["email"]
        password = data["password"]
        user_type = data["type"]

        # ---- Block reserved guest usernames ----
        if username in ["andrey", "kevin"]:
            return Response(
                {"error": "This username is reserved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the new Django user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create corresponding profile based on user_type
        if user_type == "customer":
            CustomerProfile.objects.create(user=user, type="customer")
        else:
            BusinessProfile.objects.create(user=user, type="business")

        # Generate or retrieve authentication token
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login. Authenticates credentials or provisions guest accounts,
    then returns an authentication token.
    """
    def post(self, request):
        """
        Handle user login.

        Expects 'username' and 'password' in request.data.
        Supports guest login for reserved usernames.
        Returns auth token and basic user info on success.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

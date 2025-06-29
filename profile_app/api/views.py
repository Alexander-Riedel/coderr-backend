from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User
from profile_app.models import BusinessProfile, CustomerProfile
from profile_app.api.serializers import BusinessProfileSerializer, CustomerProfileSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserProfileDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, pk):
        profile = BusinessProfile.objects.filter(user_id=pk).first()
        if profile:
            return profile, 'business'
        profile = CustomerProfile.objects.filter(user_id=pk).first()
        if profile:
            return profile, 'customer'
        return None, None

    def get(self, request, pk):
        profile, profile_type = self.get_profile(pk)
        if not profile:
            return Response({"detail": "Profil nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        serializer_class = BusinessProfileSerializer if profile_type == 'business' else CustomerProfileSerializer
        data = serializer_class(profile).data

        user = profile.user
        data['email'] = user.email or ''
        data['created_at'] = user.date_joined.isoformat()

        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            if data.get(field) is None:
                data[field] = ""

        return Response(data)

    def patch(self, request, pk):
        if request.user.id != pk:
            return Response({"detail": "Du darfst nur dein eigenes Profil bearbeiten."}, status=status.HTTP_403_FORBIDDEN)

        profile, profile_type = self.get_profile(pk)
        if not profile:
            return Response({"detail": "Profil nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        serializer_class = BusinessProfileSerializer if profile_type == 'business' else CustomerProfileSerializer
        serializer = serializer_class(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            new_email = request.data.get('email')
            if new_email:
                user = profile.user
                user.email = new_email
                user.save()

            data = serializer.data
            data['email'] = profile.user.email
            data['created_at'] = profile.user.date_joined.isoformat()

            for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                if data.get(field) is None:
                    data[field] = ""

            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(ListAPIView):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        if isinstance(results, list):
            for item in results:
                for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                    if item.get(field) is None:
                        item[field] = ""
        return response


class CustomerProfileListView(ListAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        if isinstance(results, list):
            for item in results:
                for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                    if item.get(field) is None:
                        item[field] = ""
        return response

"""
Module profile_app.api.views

Implements API views for retrieving and updating user profiles,
and listing business and customer profiles.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User

from profile_app.models import BusinessProfile, CustomerProfile
from profile_app.api.serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer
)


class IsOwner(permissions.BasePermission):
    """
    Permission that grants access only if the requesting user
    is the owner of the profile object.
    """
    def has_object_permission(self, request, view, obj):
        # Allow action only if the profile belongs to the authenticated user
        return obj.user == request.user


class UserProfileDetailView(APIView):
    """
    Retrieve or update a single user profile (business or customer).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, pk):
        """
        Internal helper to fetch a profile by user ID.

        Returns:
            tuple(profile_instance, profile_type) or (None, None) if not found.
        """
        # Try BusinessProfile first
        profile = BusinessProfile.objects.filter(user_id=pk).first()
        if profile:
            return profile, 'business'
        # Then try CustomerProfile
        profile = CustomerProfile.objects.filter(user_id=pk).first()
        if profile:
            return profile, 'customer'
        # No profile found
        return None, None

    def get(self, request, pk):
        """
        Handle GET /api/profile/{pk}/:
        - Return profile data for the given user ID.
        """
        profile, profile_type = self.get_profile(pk)
        if not profile:
            return Response(
                {"detail": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Choose serializer based on profile type
        serializer_cls = (
            BusinessProfileSerializer
            if profile_type == 'business'
            else CustomerProfileSerializer
        )
        data = serializer_cls(profile).data

        # Add email and account creation timestamp
        user = profile.user
        data['email'] = user.email or ''
        data['created_at'] = user.date_joined.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Ensure optional text fields are non-null strings
        for field in [
            'first_name', 'last_name', 'location', 'tel',
            'description', 'working_hours'
        ]:
            if data.get(field) is None:
                data[field] = ""

        return Response(data)

    def patch(self, request, pk):
        """
        Handle PATCH /api/profile/{pk}/:
        - Allow only the profile owner to update their own profile.
        """
        # Prevent editing someone else's profile
        if request.user.id != pk:
            return Response(
                {"detail": "You may only edit your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile, profile_type = self.get_profile(pk)
        if not profile:
            return Response(
                {"detail": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Use the appropriate serializer for partial update
        serializer_cls = (
            BusinessProfileSerializer
            if profile_type == 'business'
            else CustomerProfileSerializer
        )
        serializer = serializer_cls(profile, data=request.data, partial=True)

        if serializer.is_valid():
            # Save updated profile fields
            serializer.save()

            # Optionally update the User's email if provided
            new_email = request.data.get('email')
            if new_email:
                user = profile.user
                user.email = new_email
                user.save()

            data = serializer.data
            data['email'] = profile.user.email
            data['created_at'] = profile.user.date_joined.strftime('%Y-%m-%dT%H:%M:%SZ')

            # Normalize optional fields
            for field in [
                'first_name', 'last_name', 'location', 'tel',
                'description', 'working_hours'
            ]:
                if data.get(field) is None:
                    data[field] = ""

            return Response(data)

        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(ListAPIView):
    """
    List all business user profiles.
    """
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # no pagination for profile lists

    def list(self, request, *args, **kwargs):
        """
        Override to ensure optional profile fields are always non-null strings.
        """
        response = super().list(request, *args, **kwargs)
        # Handle both paginated and non-paginated responses
        results = (
            response.data
            if isinstance(response.data, list)
            else response.data.get('results', [])
        )
        if isinstance(results, list):
            for item in results:
                for field in [
                    'first_name', 'last_name', 'location', 'tel',
                    'description', 'working_hours'
                ]:
                    if item.get(field) is None:
                        item[field] = ""
        return response


class CustomerProfileListView(ListAPIView):
    """
    List all customer user profiles.
    """
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # no pagination for profile lists

    def list(self, request, *args, **kwargs):
        """
        Override to ensure optional profile fields are always non-null strings.
        """
        response = super().list(request, *args, **kwargs)
        for item in response.data:
            for field in ('first_name', 'last_name'):
                if item.get(field) is None:
                    item[field] = ""
        return response
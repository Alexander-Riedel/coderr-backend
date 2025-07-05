from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from profile_app.models import BusinessProfile, CustomerProfile
from profile_app.api.serializers import (
    ProfileDetailSerializer,
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
)


class ProfileDetailView(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileDetailSerializer
    lookup_field = 'user_id'  # wir nehmen user_id als URL-Parameter

    def get_object(self):
        user_id = self.kwargs['user_id']
        # erst BusinessProfile, dann CustomerProfile
        obj = BusinessProfile.objects.filter(user_id=user_id).first()
        if not obj:
            obj = CustomerProfile.objects.filter(user_id=user_id).first()
        if not obj:
            # 404
            self.permission_denied(self.request, message="Profil nicht gefunden.")
        # Owner-Check (RetrieveUpdateAPIView ruft check_object_permissions)
        self.check_object_permissions(self.request, obj)
        return obj

    def patch(self, request, *args, **kwargs):
        # Owner darf patchen
        obj = self.get_object()
        if obj.user_id != request.user.id:
            return Response({"detail": "Nur eigenes Profil editierbar."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

class BusinessProfileListView(ListAPIView):
    """
    GET /api/profiles/business/
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileListSerializer
    pagination_class = None

class CustomerProfileListView(ListAPIView):
    """
    GET /api/profiles/customer/
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileListSerializer
    pagination_class = None

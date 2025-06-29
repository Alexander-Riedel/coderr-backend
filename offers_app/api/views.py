from rest_framework import generics, permissions, status, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailSerializer
from profile_app.models import BusinessProfile

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return BusinessProfile.objects.filter(user=request.user).exists()

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsBusinessUser()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        details_data = data.get('details', [])
        if not isinstance(details_data, list) or len(details_data) < 3:
            return Response({"details": "Ein Angebot muss mindestens 3 Details enthalten."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        offer = self.get_object()
        if offer.user != request.user:
            return Response({"detail": "Nur der Ersteller darf dieses Angebot bearbeiten."}, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        offer = self.get_object()
        if offer.user != request.user:
            return Response({"detail": "Nur der Ersteller darf dieses Angebot löschen."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

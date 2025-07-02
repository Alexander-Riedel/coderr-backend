from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from orders_app.models import Order
from offers_app.models import OfferDetail
from profile_app.models import CustomerProfile, BusinessProfile
from orders_app.api.serializers import OrderSerializer

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404


# --- List & Create: /api/orders/ ---
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Nur Orders, bei denen der User beteiligt ist
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = request.user
        # Check: nur Kunden dürfen bestellen
        if not CustomerProfile.objects.filter(user=user).exists():
            return Response({"detail": "Nur Kunden dürfen Bestellungen anlegen."}, status=status.HTTP_403_FORBIDDEN)

        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({"detail": "offer_detail_id erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer_detail = OfferDetail.objects.select_related('offer', 'offer__user').get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({"detail": "OfferDetail nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        # Bestellungsdaten aus dem OfferDetail
        order = Order.objects.create(
            customer_user=user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status=request.data.get('status', 'in_progress'),
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# --- Retrieve, Update, Delete: /api/orders/{id}/ ---
class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        # Nur business_user darf Status ändern
        if 'status' in request.data and user != order.business_user:
            return Response({"detail": "Nur der Geschäftspartner darf den Status ändern."}, status=status.HTTP_403_FORBIDDEN)

        # Nur Status darf geändert werden (alle anderen Felder read_only)
        allowed_fields = {'status'}
        if any(field not in allowed_fields for field in request.data.keys()):
            return Response({"detail": "Nur das Feld 'status' darf geändert werden."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        # Nur Staff/Admin kann löschen
        if not user.is_staff:
            return Response({"detail": "Nur Admins dürfen Bestellungen löschen."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

# --- Zähler-Endpoints ---
from rest_framework.views import APIView

class OrderCountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        # 1) Existenz prüfen
        business = get_object_or_404(User, id=business_user_id, businessprofile__isnull=False)
        # 2) Zählen
        count = Order.objects.filter(business_user=business, status='in_progress').count()
        return Response({"order_count": count})

class CompletedOrderCountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        # 1) Prüfen, ob es ein BusinessProfile für diese user_id gibt – sonst 404
        get_object_or_404(BusinessProfile, user_id=business_user_id)

        # 2) Anzahl abgeschlossener Bestellungen zählen
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status='completed'
        ).count()

        return Response(
            {"completed_order_count": count},
            status=status.HTTP_200_OK
        )

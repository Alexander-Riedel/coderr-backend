"""
Module orders_app.api.views

Implements API views for listing, creating, retrieving, updating, and deleting orders,
as well as endpoints to count in-progress and completed orders for business users.
"""

from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from orders_app.models import Order
from offers_app.models import OfferDetail
from profile_app.models import CustomerProfile, BusinessProfile
from orders_app.api.serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/orders/ → List all orders in which the current user is involved
    POST /api/orders/ → Create a new order (only for users with a CustomerProfile)
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None  # no pagination for orders
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return orders where the request.user is either the customer or the business.
        Orders are sorted by creation time descending.
        """
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = request.user

        # Nur Kunden dürfen bestellen
        if not CustomerProfile.objects.filter(user=user).exists():
            return Response(
                {"detail": "Only customers may create orders."},
                status=status.HTTP_403_FORBIDDEN
            )

        # offer_detail_id validieren
        od_id = request.data.get('offer_detail_id')
        if od_id is None:
            return Response(
                {"offer_detail_id": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            od_id = int(od_id)
        except (TypeError, ValueError):
            return Response(
                {"offer_detail_id": "Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OfferDetail laden oder 404
        offer_detail = get_object_or_404(OfferDetail, id=od_id)

        # Bestellung anlegen
        order = Order.objects.create(
            customer_user          = user,
            business_user          = offer_detail.offer.user,
            title                  = offer_detail.title,
            revisions              = offer_detail.revisions,
            delivery_time_in_days  = offer_detail.delivery_time_in_days,
            price                  = offer_detail.price,
            features               = offer_detail.features,
            offer_type             = offer_detail.offer_type,
            status                 = 'in_progress',
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/orders/{id}/    → Retrieve a single order by its ID
    PATCH  /api/orders/{id}/    → Update only the 'status' field (business user only)
    DELETE /api/orders/{id}/    → Delete an order (staff users only)
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Allow the business_user to update the status of an order.
        Reject any changes to fields other than 'status'.
        """
        order = self.get_object()
        user = request.user
        data = request.data

        # Only the business participant may change the order status
        if 'status' in data and user != order.business_user:
            return Response(
                {"detail": "Only the business user may change the status."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Only 'status' field is writable; all others are read-only
        if any(field not in ('status',) for field in data):
            return Response(
                {"detail": "Only the 'status' field may be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check valide status
        valid_statuses = ['in_progress', 'completed', 'cancelled']
        new_status = data.get('status')
        if new_status not in valid_statuses:
            return Response(
                {"status": f"Ungültiger status. Erwartet einer von {valid_statuses}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(order, data={'status': new_status}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Allow deletion of an order only by staff/admin users.
        """
        order = self.get_object()
        user = request.user

        if not user.is_staff:
            return Response(
                {"detail": "Only staff users may delete orders."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().delete(request, *args, **kwargs)


# --- Count endpoints for business users ---
from rest_framework.views import APIView


class OrderCountView(APIView):
    """
    GET /api/order-count/{business_user_id}/
    Returns the count of in-progress orders for the specified business user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        # Verify that the user exists and has a BusinessProfile
        business = get_object_or_404(User, id=business_user_id, businessprofile__isnull=False)

        # Count orders with status 'in_progress'
        count = Order.objects.filter(
            business_user=business,
            status='in_progress'
        ).count()

        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    """
    GET /api/completed-order-count/{business_user_id}/
    Returns the count of completed orders for the specified business user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        # Ensure the business profile exists for this user_id (404 otherwise)
        get_object_or_404(BusinessProfile, user_id=business_user_id)

        # Count orders with status 'completed'
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status='completed'
        ).count()

        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)

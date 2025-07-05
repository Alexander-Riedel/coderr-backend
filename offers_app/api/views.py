from rest_framework import generics, permissions, status, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from django.db import models

from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailSerializer
from profile_app.models import BusinessProfile


class OfferPagination(PageNumberPagination):
    """
    Custom pagination class allowing client to set page size via 'page_size' query parameter.
    """
    page_size_query_param = 'page_size'


class IsBusinessUser(permissions.BasePermission):
    """
    Permission class to allow only business users to create or modify offers.

    Checks if the requesting user has an associated BusinessProfile.
    """
    def has_permission(self, request, view):
        return BusinessProfile.objects.filter(user=request.user).exists()


class OfferListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/offers/ → List all offers, with pagination, filtering, search, and ordering support.
    POST /api/offers/ → Create a new offer (requires authentication and business user),
                        with minimum of 3 detail items.
    """
    queryset = Offer.objects.all().order_by('-updated_at')
    serializer_class = OfferSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at']

    def get_permissions(self):
        """
        Dynamically assign permissions: only authenticated business users may POST.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsBusinessUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        """
        Optionally filter queryset by creator_id, min_price, max_delivery_time, search, and ordering.
        """
        qs = super().get_queryset()
        params = self.request.query_params

        # Filter by creator user ID
        if creator := params.get('creator_id'):
            qs = qs.filter(user_id=creator)

        # Filter by minimum detail price
        if minp := params.get('min_price'):
            try:
                minp_val = float(minp)
            except ValueError:
                raise ValidationError({"min_price": "Must be a number."})
            qs = qs.filter(details__price__gte=minp_val)

        # Filter by maximum delivery time
        if maxt := params.get('max_delivery_time'):
            try:
                maxt_val = int(maxt)
            except ValueError:
                raise ValidationError({"max_delivery_time": "Must be an integer."})
            qs = qs.filter(details__delivery_time_in_days__lte=maxt_val)

        # Search in title or description
        if search := params.get('search'):
            qs = qs.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )

        # Apply ordering if provided
        if order := params.get('ordering'):
            qs = qs.order_by(order)

        return qs.distinct()

    def create(self, request, *args, **kwargs):
        """
        Create a new Offer instance along with its OfferDetail items.

        Validates that at least 3 detail entries are provided, assigns current user,
        and returns the newly created offer with full detail list.
        """
        data = request.data.copy()
        data['user'] = request.user.id
        details = data.get('details', [])

        # Ensure at least three detail objects
        if not isinstance(details, list) or len(details) < 3:
            return Response(
                {"details": "An offer must include at least 3 detail items."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Serialize and save the Offer
        serializer = OfferSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save(user=request.user)

        # Create OfferDetail entries
        for detail_data in details:
            OfferDetail.objects.create(offer=offer, **detail_data)

        # Build full response including details
        full_details = OfferDetail.objects.filter(offer=offer)
        detail_data = OfferDetailSerializer(full_details, many=True).data

        response_data = {
            "id": offer.id,
            "title": offer.title,
            "image": offer.image.url if offer.image else None,
            "description": offer.description,
            "details": detail_data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/offers/{id}/   → Retrieve offer details.
    PATCH  /api/offers/{id}/   → Update main fields and optional details (only creator).
    DELETE /api/offers/{id}/   → Delete the offer (only creator).
    """
    queryset = Offer.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override, um fehlende Objekte als Bad Request (400) statt Not Found (404)
        zurückzugeben.
        """
        try:
            return super().get_object()
        except Http404:
            # wandeln wir Http404 in einen 400 Bad Request um
            raise ValidationError({"detail": "Ungültige Angebots-ID."})

    def get_serializer_class(self):
        """
        Return the serializer class for this view. Customize if needed.
        """
        return OfferSerializer

    def patch(self, request, *args, **kwargs):
        """
        Partially update the Offer and its related details.

        Only the original creator may apply changes. Validates detail list if provided.
        """
        offer = self.get_object()

        # Permission check: only creator
        if offer.user != request.user:
            return Response(
                {"detail": "Only the creator may edit this offer."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update main fields
        main_serializer = OfferSerializer(offer, data=request.data, partial=True)
        main_serializer.is_valid(raise_exception=True)
        main_serializer.save()

        # Update related OfferDetail entries if provided
        details_data = request.data.get('details')
        if details_data is not None:
            if not isinstance(details_data, list):
                return Response(
                    {"details": "Expected a list of detail objects."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            for d in details_data:
                # Identify detail by offer_type
                offer_type = d.get('offer_type')
                if not offer_type:
                    return Response(
                        {"offer_type": "offer_type field required to identify detail."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    det = OfferDetail.objects.get(offer=offer, offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    return Response(
                        {"details": f"No detail found for offer_type '{offer_type}'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Update fields on the detail object
                for field in ['title', 'revisions', 'delivery_time_in_days', 'price', 'features']:
                    if field in d:
                        setattr(det, field, d[field])
                det.save()

        # Rebuild response with updated details
        full_details = OfferDetail.objects.filter(offer=offer)
        detail_data = OfferDetailSerializer(full_details, many=True).data

        response_data = {
            "id": offer.id,
            "title": offer.title,
            "image": offer.image.url if offer.image else None,
            "description": offer.description,
            "details": detail_data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Delete the Offer instance. Only the creator may delete.
        """
        offer = self.get_object()
        if offer.user != request.user:
            return Response(
                {"detail": "Only the creator may delete this offer."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    GET /api/offerdetails/{id}/ → Retrieve a single OfferDetail instance.

    Returns fields: features, price, delivery_time_in_days, and offer_type.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

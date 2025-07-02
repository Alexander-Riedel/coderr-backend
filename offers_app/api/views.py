from rest_framework import generics, permissions, status, serializers, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db import models

from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailSerializer
from profile_app.models import BusinessProfile


class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class IsBusinessUser(permissions.BasePermission):
    """Nur business-Profile dürfen Offers anlegen."""
    def has_permission(self, request, view):
        return BusinessProfile.objects.filter(user=request.user).exists()


# -------------------------------------------------------------------
# 1) LIST + CREATE /api/offers/   (GET & POST)
# -------------------------------------------------------------------
class OfferListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/offers/     → Liste aller Offers (paginiert, filter-, search-, ordering-Parameter)
    POST /api/offers/     → Neues Offer anlegen (min. 3 Details, nur BusinessUser)
    """
    queryset = Offer.objects.all().order_by('-updated_at')
    serializer_class = OfferSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = []
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsBusinessUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        if creator := params.get('creator_id'):
            qs = qs.filter(user_id=creator)
        if minp := params.get('min_price'):
            qs = qs.filter(details__price__gte=minp)
        if maxt := params.get('max_delivery_time'):
            qs = qs.filter(details__delivery_time_in_days__lte=maxt)
        if search := params.get('search'):
            qs = qs.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )
        if order := params.get('ordering'):
            qs = qs.order_by(order)

        return qs.distinct()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        details = data.get('details', [])
        if not isinstance(details, list) or len(details) < 3:
            return Response(
                {"details": "Ein Angebot muss mindestens 3 Details enthalten."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) Offer anlegen
        serializer = OfferSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save(user=request.user)

        # 2) Detail-Instanzen anlegen
        for detail_data in details:
            OfferDetail.objects.create(offer=offer, **detail_data)

        # 3) Kompletten POST-Response manuell aufbauen
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


# -------------------------------------------------------------------
# 2) RETRIEVE / PATCH / DELETE  /api/offers/{pk}/
# -------------------------------------------------------------------
class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/offers/{id}/   → Detail-Ansicht (keine Änderung hier)
    PATCH  /api/offers/{id}/   → Patch + manuelle Response
    DELETE /api/offers/{id}/   → Löschen
    """
    queryset = Offer.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # def get_permissions(self):
    #     if self.request.method in ('PATCH', 'DELETE'):
    #         return [permissions.IsAuthenticated()]
    #     return [permissions.AllowAny()]

    def get_serializer_class(self):
        # Für GET könnte hier OfferRetrieveSerializer stehen,
        # wir behandeln PATCH und DELETE gesondert
        return OfferSerializer

    def patch(self, request, *args, **kwargs):
        offer = self.get_object()

        # Nur der Ersteller darf patchen
        if offer.user != request.user:
            return Response(
                {"detail": "Nur der Ersteller darf dieses Angebot bearbeiten."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 1) Hauptfelder patchen
        main_serializer = OfferSerializer(offer, data=request.data, partial=True)
        main_serializer.is_valid(raise_exception=True)
        main_serializer.save()

        # 2) Details updaten, falls geliefert
        details_data = request.data.get('details')
        if details_data is not None:
            if not isinstance(details_data, list):
                return Response(
                    {"details": "Erwarte eine Liste von Details."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            for d in details_data:
                offer_type = d.get('offer_type')
                if not offer_type:
                    return Response(
                        {"offer_type": "offer_type zum Identifizieren erforderlich."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    det = OfferDetail.objects.get(offer=offer, offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    return Response(
                        {"details": f"Kein Detail für offer_type '{offer_type}' gefunden."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                for field in ['title', 'revisions', 'delivery_time_in_days', 'price', 'features']:
                    if field in d:
                        setattr(det, field, d[field])
                det.save()

        # 3) Manuelle Response: nur die geforderten Felder
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
        offer = self.get_object()
        if offer.user != request.user:
            return Response(
                {"detail": "Nur der Ersteller darf dieses Angebot löschen."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


# -------------------------------------------------------------------
# 3) RETRIEVE EINZELNES OfferDetail
# -------------------------------------------------------------------
class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    GET /api/offerdetails/{id}/
    Einzelnes OfferDetail (Features, price, delivery_time_in_days, offer_type)
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

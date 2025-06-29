from rest_framework import generics, permissions, status, serializers, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer
from profile_app.models import BusinessProfile
from rest_framework.pagination import PageNumberPagination
from django.db import models


class OfferPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return BusinessProfile.objects.filter(user=request.user).exists()

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at']
    pagination_class = OfferPagination

    def get_queryset(self):
        queryset = Offer.objects.all()

        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)

        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            queryset = queryset.filter(details__delivery_time_in_days__lte=max_delivery_time)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(models.Q(title__icontains=search) | models.Q(description__icontains=search))

        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset.distinct()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsBusinessUser()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        details_data = data.get('details', [])
        if not isinstance(details_data, list) or len(details_data) < 3:
            return Response({"details": "Ein Angebot muss mindestens 3 Details enthalten."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

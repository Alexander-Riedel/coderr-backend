from rest_framework import generics, permissions, status, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from profile_app.models import CustomerProfile


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if bu := params.get('business_user_id'):
            qs = qs.filter(business_user_id=bu)
        if rv := params.get('reviewer_id'):
            qs = qs.filter(reviewer_id=rv)
        return qs

    def post(self, request, *args, **kwargs):
        if not CustomerProfile.objects.filter(user=request.user).exists():
            return Response({"detail": "Nur Kunden dürfen Bewertungen erstellen."}, status=status.HTTP_403_FORBIDDEN)

        business_user = request.data.get('business_user')
        if Review.objects.filter(business_user_id=business_user, reviewer=request.user).exists():
            return Response({"detail": "Du hast bereits für dieses Business bewertet."}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ('PATCH', 'DELETE') and obj.reviewer != request.user:
            self.permission_denied(request, message="Nur der Ersteller darf diese Bewertung ändern.")
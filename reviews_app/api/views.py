"""
Module reviews_app.api.views

Implements API views for listing, creating, retrieving, updating, and deleting reviews.
Provides filtering by business user or reviewer, and ensures only customers can create reviews
and only the original reviewer can modify or delete their review.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from profile_app.models import CustomerProfile


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/reviews/ → List all reviews (supports ordering by updated_at or rating)
    POST /api/reviews/ → Create a new review (only for users with a CustomerProfile and not already reviewed)
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    pagination_class = None  # disable pagination for simplicity

    def get_queryset(self):
        """
        Optionally filter reviews by business_user_id or reviewer_id query parameters.
        """
        qs = super().get_queryset()
        params = self.request.query_params

        # Filter by the reviewed business user
        if business_id := params.get('business_user_id'):
            qs = qs.filter(business_user_id=business_id)

        # Filter by the reviewer
        if reviewer_id := params.get('reviewer_id'):
            qs = qs.filter(reviewer_id=reviewer_id)

        return qs

    def post(self, request, *args, **kwargs):
        """
        Ensure only customers can create reviews and prevent duplicate reviews
        for the same business by the same reviewer.
        """
        # Only users with a CustomerProfile may post reviews
        if not CustomerProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Only customers may create reviews."},
                status=status.HTTP_403_FORBIDDEN
            )

        business_user = request.data.get('business_user')
        # Prevent duplicate reviews for the same business user
        if Review.objects.filter(
            business_user_id=business_user,
            reviewer=request.user
        ).exists():
            return Response(
                {"detail": "You have already reviewed this business."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delegate to ListCreateAPIView.post for actual creation
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Attach the current user as the 'reviewer' before saving.
        """
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/reviews/{id}/    → Retrieve a single review by its ID
    PATCH  /api/reviews/{id}/    → Partially update a review (only by the original reviewer)
    DELETE /api/reviews/{id}/    → Delete a review (only by the original reviewer)
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        """
        Extend default permissions to ensure only the original reviewer
        may update or delete their review.
        """
        super().check_object_permissions(request, obj)

        # For PATCH and DELETE, enforce reviewer-only access
        if request.method in ('PATCH', 'DELETE') and obj.reviewer != request.user:
            self.permission_denied(
                request,
                message="Only the original reviewer may modify or delete this review."
            )

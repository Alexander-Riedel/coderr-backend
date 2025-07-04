from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from reviews_app.models import Review
from profile_app.models import BusinessProfile
from offers_app.models import Offer


class BaseInfoView(APIView):
    """
    API endpoint for aggregated site-wide statistics.

    Provides total counts and average rating for the main entities:
    - Reviews
    - Business profiles
    - Offers
    """
    permission_classes = []  # Allow unrestricted access

    def get(self, request):
        """
        Retrieve base information metrics.

        Returns:
            - review_count: Total number of reviews.
            - average_rating: Average review rating (1 decimal place).
            - business_profile_count: Total number of business profiles.
            - offer_count: Total number of offers.

        On error, returns HTTP 500 with error detail.
        """
        try:
            # Total number of reviews
            review_count = Review.objects.count()

            # Calculate average rating, defaulting to 0.0 if no reviews
            average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
            average_rating = round(average_rating, 1)

            # Total number of business profiles
            business_profile_count = BusinessProfile.objects.count()

            # Total number of offers
            offer_count = Offer.objects.count()

            # Build and return response data
            return Response({
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count
            }, status=status.HTTP_200_OK)

        except Exception:
            # Catch-all for unexpected errors
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

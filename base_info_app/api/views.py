from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from reviews_app.models import Review  # <- Passe ggf. den Pfad/Modul an
from profile_app.models import BusinessProfile  # <- Passe ggf. den Pfad/Modul an
from offers_app.models import Offer  # <- Passe ggf. den Pfad/Modul an


class BaseInfoView(APIView):
    permission_classes = []  # kein Login nötig

    def get(self, request):
        try:
            review_count = Review.objects.count()
            average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
            average_rating = round(average_rating, 1)

            business_profile_count = BusinessProfile.objects.count()
            offer_count = Offer.objects.count()

            return Response({
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

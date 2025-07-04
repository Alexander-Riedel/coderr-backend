from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from profile_app.models import BusinessProfile, CustomerProfile


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Provides only the ID and absolute URL for each OfferDetail, suitable for list overviews.

    Fields:
        id: Unique identifier of the OfferDetail.
        url: Full URI to retrieve the OfferDetail detail view.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Construct the absolute URL for the OfferDetail endpoint.

        Args:
            obj (OfferDetail): The OfferDetail instance.

        Returns:
            str: Absolute URL for retrieving this OfferDetail.
        """
        request = self.context.get('request')
        path = f"/api/offerdetails/{obj.id}/"
        return request.build_absolute_uri(path) if request else path


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Full representation of an OfferDetail for detailed views and update responses.

    Includes all relevant fields of the OfferDetail model.
    """

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for Offers in list, create, and update endpoints.

    - details: List of related OfferDetailLinkSerializer items (read-only).
    - min_price: Lowest price among related details.
    - min_delivery_time: Shortest delivery time among related details.
    - user_details: Basic info about the offer creator from their profile.
    """
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]

    def get_min_price(self, obj):
        """
        Compute the lowest price among this Offer's details.

        Args:
            obj (Offer): The Offer instance.

        Returns:
            float or None: Minimum price, or None if no details exist.
        """
        details = obj.details.order_by('price')
        return float(details.first().price) if details.exists() else None

    def get_min_delivery_time(self, obj):
        """
        Compute the shortest delivery time among this Offer's details.

        Args:
            obj (Offer): The Offer instance.

        Returns:
            int or None: Minimum delivery_time_in_days, or None if no details exist.
        """
        details = obj.details.order_by('delivery_time_in_days')
        return details.first().delivery_time_in_days if details.exists() else None

    def get_user_details(self, obj):
        """
        Retrieve brief profile information for the offer creator.

        Checks for a BusinessProfile first, then CustomerProfile.

        Args:
            obj (Offer): The Offer instance.

        Returns:
            dict: Contains 'first_name', 'last_name', 'username', or empty dict if no profile.
        """
        profile = (
            BusinessProfile.objects.filter(user=obj.user).first() or
            CustomerProfile.objects.filter(user=obj.user).first()
        )
        if profile:
            return {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'username': profile.username,
            }
        return {}


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Offer view (GET /api/offers/{id}/).

    Similar to OfferSerializer but excludes user_details.
    """
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
        ]

    def get_min_price(self, obj):
        """
        Compute the lowest price among this Offer's details.
        """
        details = obj.details.order_by('price')
        return float(details.first().price) if details.exists() else None

    def get_min_delivery_time(self, obj):
        """
        Compute the shortest delivery time among this Offer's details.
        """
        details = obj.details.order_by('delivery_time_in_days')
        return details.first().delivery_time_in_days if details.exists() else None

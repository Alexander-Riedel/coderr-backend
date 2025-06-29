from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from profile_app.models import BusinessProfile, CustomerProfile


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Liefert nur ID und absolute URL für jedes OfferDetail (für Listen/Überblick).
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/offerdetails/{obj.id}/")
        return f"/api/offerdetails/{obj.id}/"


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Volle Darstellung eines OfferDetail, z.B. für PATCH-Response.
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
    Serializer für Create/Update und Listen-Views.
    - details: nur Link-Version
    - user_details: kurzinfo zum Ersteller
    - min_price / min_delivery_time: erste bzw. günstigste/r schnellste Detail-Option
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
        if obj.details.exists():
            return float(obj.details.order_by('price').first().price)
        return None

    def get_min_delivery_time(self, obj):
        if obj.details.exists():
            return obj.details.order_by('delivery_time_in_days').first().delivery_time_in_days
        return None

    def get_user_details(self, obj):
        # Prüfe Business-Profile zuerst, dann Customer
        profile = (
            BusinessProfile.objects.filter(user=obj.user).first() or
            CustomerProfile.objects.filter(user=obj.user).first()
        )
        if profile:
            return {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'username': profile.username
            }
        return {}


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer für Detail-View (GET /api/offers/{id}/).
    - details: nur Link-Version
    - min_price / min_delivery_time
    (kein user_details hier, weil nicht gefordert)
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
        if obj.details.exists():
            return float(obj.details.order_by('price').first().price)
        return None

    def get_min_delivery_time(self, obj):
        if obj.details.exists():
            return obj.details.order_by('delivery_time_in_days').first().delivery_time_in_days
        return None

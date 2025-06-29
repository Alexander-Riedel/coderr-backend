from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from profile_app.models import BusinessProfile, CustomerProfile

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/offerdetails/{obj.id}/")
        return f"/api/offerdetails/{obj.id}/"


class OfferSerializer(serializers.ModelSerializer):
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

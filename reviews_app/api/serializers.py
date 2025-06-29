from rest_framework import serializers
from django.contrib.auth.models import User
from profile_app.models import CustomerProfile, BusinessProfile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    rating = serializers.IntegerField(min_value=1, max_value=5)
    description = serializers.CharField(allow_blank=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate_business_user(self, value):
        # Sicherstellen, dass der business_user ein BusinessProfile hat
        if not BusinessProfile.objects.filter(user=value).exists():
            raise serializers.ValidationError("business_user muss ein Business-Profil besitzen.")
        return value

    def validate(self, data):
        # Prüfen, ob der Rezensent ein CustomerProfile hat
        user = self.context['request'].user
        if not CustomerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError("Nur Kunden dürfen Bewertungen schreiben.")
        # Prüfen, ob bereits eine Bewertung existiert
        if self.instance is None:  # nur bei POST
            existing = Review.objects.filter(
                business_user=data['business_user'],
                reviewer=user
            ).exists()
            if existing:
                raise serializers.ValidationError("Du hast bereits eine Bewertung für diesen Nutzer abgegeben.")
        return data

    def create(self, validated_data):
        reviewed_user = validated_data['business_user']
        reviewer = self.context['request'].user
        review = Review.objects.create(
            business_user=reviewed_user,
            reviewer=reviewer,
            rating=validated_data['rating'],
            description=validated_data.get('description', '')
        )
        return review

    def update(self, instance, validated_data):
        # Nur rating und description dürfen bearbeitet werden
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

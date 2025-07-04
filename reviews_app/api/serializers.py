"""
Module reviews_app.api.serializers

Defines the ReviewSerializer for converting Review model instances
to and from JSON for the reviews API. Enforces business and customer
profile constraints and prevents duplicate reviews.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from profile_app.models import CustomerProfile, BusinessProfile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review objects.

    - 'reviewer' is set automatically to the requesting user (read-only).
    - 'business_user' must reference a User with an existing BusinessProfile.
    - 'rating' must be between 1 and 5.
    - 'description' may be blank.
    """
    # The user who wrote the review; set in view logic, not by client
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    # The business user receiving the review; must exist as BusinessProfile
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # Integer rating field, constrained to 1–5
    rating = serializers.IntegerField(min_value=1, max_value=5)
    # Optional text feedback
    description = serializers.CharField(allow_blank=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]
        # Prevent clients from modifying these fields
        read_only_fields = [
            'id',
            'reviewer',
            'created_at',
            'updated_at',
        ]

    def validate_business_user(self, value):
        """
        Ensure the provided business_user has an associated BusinessProfile.
        """
        if not BusinessProfile.objects.filter(user=value).exists():
            raise serializers.ValidationError(
                "business_user must have an associated BusinessProfile."
            )
        return value

    def validate(self, data):
        """
        Cross-field validation:
        - Only users with a CustomerProfile may create reviews.
        - Prevent duplicate reviews by the same reviewer for the same business_user.
        """
        user = self.context['request'].user

        # Only customers may write reviews
        if not CustomerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                "Only customers may write reviews."
            )

        # On creation, prevent duplicates
        if self.instance is None:
            exists = Review.objects.filter(
                business_user=data['business_user'],
                reviewer=user
            ).exists()
            if exists:
                raise serializers.ValidationError(
                    "You have already reviewed this business user."
                )

        return data

    def create(self, validated_data):
        """
        Create a new Review instance, setting the reviewer to the requesting user.
        """
        reviewed_user = validated_data['business_user']
        reviewer = self.context['request'].user
        return Review.objects.create(
            business_user=reviewed_user,
            reviewer=reviewer,
            rating=validated_data['rating'],
            description=validated_data.get('description', '')
        )

    def update(self, instance, validated_data):
        """
        Update only the rating and description fields on an existing review.
        """
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        instance.save()
        return instance

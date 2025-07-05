"""
Module profile_app.api.serializers

Defines serializers for BusinessProfile and CustomerProfile models,
controlling how profile data is converted to/from JSON for API requests and responses.
"""

from rest_framework import serializers
from profile_app.models import BusinessProfile, CustomerProfile


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for BusinessProfile instances.

    - 'user' and 'username' are read-only and populated by the server.
    - All other fields are writable to allow profile updates.
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(default='', read_only=True)
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    file = serializers.FileField(required=False, allow_null=True)
    location = serializers.CharField(default='')
    tel = serializers.CharField(default='')
    description = serializers.CharField(default='')
    working_hours = serializers.CharField(default='')
    type = serializers.CharField(default='business')

    class Meta:
        model = BusinessProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerProfile instances.

    - 'user' and 'username' are read-only and populated by the server.
    - All other fields are writable to allow profile updates.
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(default='', read_only=True)
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    file = serializers.FileField(required=False, allow_null=True)
    uploaded_at = serializers.DateTimeField(
        source='user.date_joined',
        format='%Y-%m-%dT%H:%M:%S',
        read_only=True
    )
    type = serializers.CharField(default='customer')

    class Meta:
        model = CustomerProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type',
        ]

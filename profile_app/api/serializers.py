"""
Module profile_app.api.serializers

Defines serializers for BusinessProfile and CustomerProfile models,
controlling how profile data is converted to/from JSON for API requests and responses.
"""

from rest_framework import serializers
from profile_app.models import BusinessProfile, CustomerProfile


class ProfileDetailSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(source='user.date_joined', format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    first_name = serializers.CharField(allow_blank=True, default='')
    last_name = serializers.CharField(allow_blank=True, default='')
    location = serializers.CharField(allow_blank=True, default='')
    tel = serializers.CharField(allow_blank=True, default='')
    description = serializers.CharField(allow_blank=True, default='')
    working_hours = serializers.CharField(allow_blank=True, default='')
    file = serializers.FileField(required=False, allow_null=True)
    type = serializers.CharField(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours',
            'type', 'email', 'created_at',
        ]

class BusinessProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(allow_blank=True, default='')
    last_name = serializers.CharField(allow_blank=True, default='')
    location = serializers.CharField(allow_blank=True, default='')
    tel = serializers.CharField(allow_blank=True, default='')
    description = serializers.CharField(allow_blank=True, default='')
    working_hours = serializers.CharField(allow_blank=True, default='')
    file = serializers.FileField(required=False, allow_null=True)
    type = serializers.CharField(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        ]

class CustomerProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(allow_blank=True, default='')
    last_name = serializers.CharField(allow_blank=True, default='')
    file = serializers.FileField(required=False, allow_null=True)
    uploaded_at = serializers.DateTimeField(source='user.date_joined', format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    type = serializers.CharField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'user', 'username', 'first_name', 'last_name',
            'file', 'uploaded_at', 'type',
        ]
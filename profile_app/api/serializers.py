from rest_framework import serializers
from profile_app.models import BusinessProfile, CustomerProfile


class BusinessProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(default='')
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    location = serializers.CharField(default='')
    tel = serializers.CharField(default='')
    description = serializers.CharField(default='')
    working_hours = serializers.CharField(default='')
    file = serializers.FileField(required=False, allow_null=True)
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
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(default='')
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    location = serializers.CharField(default='')
    tel = serializers.CharField(default='')
    description = serializers.CharField(default='')
    working_hours = serializers.CharField(default='')
    file = serializers.FileField(required=False, allow_null=True)
    type = serializers.CharField(default='customer')

    class Meta:
        model = CustomerProfile
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

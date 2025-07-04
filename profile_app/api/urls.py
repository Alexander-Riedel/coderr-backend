"""
Module profile_app.api.urls

Defines URL routes for user profile API endpoints:
- GET/PATCH /api/profile/{pk}/       Retrieve or update a single user profile (business or customer)
- GET      /api/profiles/business/   List all business user profiles
- GET      /api/profiles/customer/   List all customer user profiles
"""

from django.urls import path
from profile_app.api.views import (
    UserProfileDetailView,
    BusinessProfileListView,
    CustomerProfileListView,
)

urlpatterns = [
    # Retrieve or update a specific user profile by its user ID
    path(
        'profile/<int:pk>/',
        UserProfileDetailView.as_view(),
        name='user-profile-detail'
    ),

    # List all business profiles (requires authentication)
    path(
        'profiles/business/',
        BusinessProfileListView.as_view(),
        name='business-profile-list'
    ),

    # List all customer profiles (requires authentication)
    path(
        'profiles/customer/',
        CustomerProfileListView.as_view(),
        name='customer-profile-list'
    ),
]

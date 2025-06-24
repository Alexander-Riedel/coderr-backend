from django.urls import path
from profile_app.api.views import (
    UserProfileDetailView,
    BusinessProfileListView,
    CustomerProfileListView,
)

urlpatterns = [
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
]

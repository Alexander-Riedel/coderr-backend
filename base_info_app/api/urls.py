from django.urls import path
from .views import BaseInfoView

# URL patterns for aggregated base information endpoints
urlpatterns = [
    # GET /api/base-info/ - retrieve overall statistics for reviews, ratings, profiles, and offers
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]
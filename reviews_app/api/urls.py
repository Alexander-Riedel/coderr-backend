"""
Module reviews_app.api.urls

Defines URL routes for review-related API endpoints:
- GET  /api/reviews/        List all reviews (supports filtering by business_user_id and reviewer_id, ordering)
- POST /api/reviews/        Create a new review (customers only, no duplicates)
- GET    /api/reviews/{id}/ Retrieve a single review by its ID
- PATCH  /api/reviews/{id}/ Partially update a review (only the original reviewer)
- DELETE /api/reviews/{id}/ Delete a review (only the original reviewer)
"""

from django.urls import path
from reviews_app.api.views import ReviewListCreateView, ReviewDetailView

urlpatterns = [
    # List existing reviews or create a new one
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),

    # Retrieve, update, or delete a specific review by its primary key
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]

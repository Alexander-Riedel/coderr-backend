from django.urls import path
from reviews_app.api.views import ReviewListCreateView, ReviewDetailView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
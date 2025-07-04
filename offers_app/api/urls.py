from django.urls import path
from offers_app.api.views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetailRetrieveView
)

"""
URL patterns for the offers API endpoints.

- /api/offers/ [GET]:   List all offers (supports pagination, filtering, search, ordering)
- /api/offers/ [POST]:  Create a new offer (requires authentication as a business user)
- /api/offers/<int:pk>/ [GET]:    Retrieve a single offer by its ID
- /api/offers/<int:pk>/ [PATCH]:  Partially update an existing offer (owner only)
- /api/offers/<int:pk>/ [DELETE]: Delete an existing offer (owner only)
- /api/offerdetails/<int:pk>/ [GET]: Retrieve details for a specific offer option
"""

urlpatterns = [
    # List existing offers or create a new one
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),

    # Retrieve, update, or delete a specific offer by its primary key
    path('offers/<int:pk>/', OfferRetrieveUpdateDestroyView.as_view(), name='offer-detail'),

    # Retrieve a single OfferDetail instance by its primary key
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]

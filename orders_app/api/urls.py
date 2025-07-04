"""
Module orders_app.api.urls

Defines URL routes for order-related API endpoints:
- /api/orders/                     [GET, POST]         List all orders for the authenticated user or create a new order (customers only)
- /api/orders/<int:pk>/            [GET, PATCH, DELETE] Retrieve, update (status), or delete an order by its ID
- /api/order-count/<int:business_user_id>/           [GET]  Count of in-progress orders for a specific business user
- /api/completed-order-count/<int:business_user_id>/ [GET]  Count of completed orders for a specific business user
"""

from django.urls import path
from orders_app.api.views import (
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView,
    OrderCountView,
    CompletedOrderCountView
)

urlpatterns = [
    # List existing orders or create a new one
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),

    # Retrieve, partially update (status), or delete an order by its primary key
    path('orders/<int:pk>/', OrderRetrieveUpdateDestroyView.as_view(), name='order-detail'),

    # Get count of orders in progress for the given business user
    path(
        'order-count/<int:business_user_id>/',
        OrderCountView.as_view(),
        name='order-count'
    ),

    # Get count of orders completed for the given business user
    path(
        'completed-order-count/<int:business_user_id>/',
        CompletedOrderCountView.as_view(),
        name='completed-order-count'
    ),
]

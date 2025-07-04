"""
Module orders_app.models

Defines the Order model representing a purchase order linking customers and business users.
"""

from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    """
    Model representing a service/order placed by a customer for a business user's offer.

    Attributes:
        customer_user (User): The user who placed the order.
        business_user (User): The user who will fulfill the order.
        title (str): Title or name of the order.
        revisions (int): Number of allowed revisions.
        delivery_time_in_days (int): Expected delivery time in days.
        price (Decimal): Price agreed for the order.
        features (list): List of feature descriptions or options.
        offer_type (str): Identifier for the type of offer selected.
        status (str): Current status of the order (e.g., 'pending', 'completed').
        created_at (datetime): Timestamp when the order was created.
        updated_at (datetime): Timestamp when the order was last updated.
    """

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_orders'
    )
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='business_orders'
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of the Order, including ID and status.
        """
        return f"Order {self.id} ({self.status})"

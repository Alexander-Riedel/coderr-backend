"""
Module reviews_app.models

Defines the Review model, representing feedback left by a customer (reviewer)
for a business user, including a unique rating and description.
"""

from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """
    Model representing a single review:
    - business_user: the user receiving the review
    - reviewer: the user who wrote the review
    - rating: an integer score (e.g., 1–5)
    - description: text feedback
    Timestamps are managed automatically.
    """

    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        null=True
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='written_reviews',
        null=True
    )
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure each reviewer can review a given business_user only once
        unique_together = ('business_user', 'reviewer')
        # Default ordering: most recently updated first
        ordering = ['-updated_at']

    def __str__(self):
        """
        Return a human-readable representation of the review,
        indicating who wrote it and who received it.
        """
        return f"Review by {self.reviewer} for {self.business_user}"

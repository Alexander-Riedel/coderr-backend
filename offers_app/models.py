from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """
    Represents an offer made by a user.

    Fields:
        user: The user who created the offer.
        title: Short title of the offer.
        image: Optional image illustrating the offer.
        description: Detailed description of the offer.
        created_at: Timestamp when the offer was created.
        updated_at: Timestamp when the offer was last updated.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='offer_images/',
        null=True,
        blank=True
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return a human-readable representation of the Offer.
        """
        return self.title


class OfferDetail(models.Model):
    """
    Detailed tier or variant information for a specific Offer.

    Fields:
        offer: The parent Offer this detail belongs to.
        title: Title of the detail tier (e.g. "Basic", "Premium").
        revisions: Number of permitted revisions included.
        delivery_time_in_days: Estimated delivery time in days.
        price: Cost for this detail tier.
        features: JSON list of additional features or bullet points.
        offer_type: Category or type label for this detail.
    """
    offer = models.ForeignKey(
        Offer,
        related_name='details',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)

    def __str__(self):
        """
        Return a string combining title and offer_type for readability.
        """
        return f"{self.title} ({self.offer_type})"

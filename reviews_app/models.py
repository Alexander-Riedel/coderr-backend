from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews', null=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_reviews', null=True)
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')
        ordering = ['-updated_at']

    def __str__(self):
        return f'Review by {self.reviewer} for {self.business_user}'

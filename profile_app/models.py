"""
Module profile_app.models

Defines user profile models for business and customer users,
extending Django's built-in User model with additional fields.
"""

from django.db import models
from django.contrib.auth.models import User


class BusinessProfile(models.Model):
    """
    Profile model for business users.

    Links one-to-one with Django's User and stores business-specific information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=255, blank=True, default='')
    file = models.FileField(upload_to='profile_images/', null=True, blank=True)
    type = models.CharField(max_length=50, default='business')


class CustomerProfile(models.Model):
    """
    Profile model for customer users.

    Links one-to-one with Django's User and stores customer-specific information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=255, blank=True, default='')
    file = models.FileField(upload_to='profile_images/', null=True, blank=True)
    type = models.CharField(max_length=50, default='customer')

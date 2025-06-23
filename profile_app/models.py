from django.db import models

class BusinessProfile(models.Model):
    name = models.CharField(max_length=100)
from django.db import models

class Offer(models.Model):
    title = models.CharField(max_length=100)
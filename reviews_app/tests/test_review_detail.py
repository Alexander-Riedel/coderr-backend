from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from reviews_app.models import Review
from profile_app.models import BusinessProfile, CustomerProfile

User = get_user_model()


class ReviewDetailTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Business, Kunde und anderer Nutzer anlegen
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')
        cls.customer = User.objects.create_user(username='cust', password='pw')
        CustomerProfile.objects.create(user=cls.customer, username='cust')
        cls.other = User.objects.create_user(username='other', password='pw')
        CustomerProfile.objects.create(user=cls.other, username='other')

        # Eine Bewertung erstellen
        cls.review = Review.objects.create(
            business_user=cls.business,
            reviewer=cls.customer,
            rating=4,
            description='Gut'
        )
        cls.url = reverse('review-detail', kwargs={'pk': cls.review.id})

    def setUp(self):
        self.client = APIClient()

    def test_patch_review_success(self):
        self.client.force_authenticate(self.customer)
        payload = {'rating': 5, 'description': 'Noch besser'}
        resp = self.client.patch(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['rating'], 5)

    def test_patch_review_forbidden(self):
        self.client.force_authenticate(self.other)
        resp = self.client.patch(self.url, {'rating': 1})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_unauthenticated(self):
        resp = self.client.patch(self.url, {'rating': 2})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_success(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_forbidden(self):
        self.client.force_authenticate(self.other)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_unauthenticated(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

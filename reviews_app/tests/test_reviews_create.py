from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from reviews_app.models import Review
from profile_app.models import BusinessProfile, CustomerProfile

User = get_user_model()


class ReviewsCreateTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Business-User und Kunden-User anlegen
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')

        cls.customer = User.objects.create_user(username='cust', password='pw')
        CustomerProfile.objects.create(user=cls.customer, username='cust')

        cls.other = User.objects.create_user(username='other', password='pw')
        CustomerProfile.objects.create(user=cls.other, username='other')

        cls.url = reverse('review-list-create')

    def setUp(self):
        self.client = APIClient()

    def test_create_review_unauthenticated(self):
        resp = self.client.post(self.url, {
            'business_user': 1, 'rating': 5, 'description': 'Test'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_forbidden_non_customer(self):
        # Business darf nicht bewerten
        self.client.force_authenticate(self.business)
        resp = self.client.post(self.url, {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Nice'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_success(self):
        self.client.force_authenticate(self.customer)
        payload = {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Alles gut'
        }
        resp = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['business_user'], self.business.id)
        self.assertEqual(resp.data['reviewer'], self.customer.id)

    def test_create_review_duplicate(self):
        self.client.force_authenticate(self.customer)
        payload = {
            'business_user': self.business.id,
            'rating': 5,
            'description': 'Toll'
        }
        # Erste Bewertung
        self.client.post(self.url, payload, format='json')
        # Zweite Bewertung für gleichen Business-User
        resp = self.client.post(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_bad_request(self):
        self.client.force_authenticate(self.customer)
        # fehlendes Feld business_user
        resp = self.client.post(self.url, {'rating': 3}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

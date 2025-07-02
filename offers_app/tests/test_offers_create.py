from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from offers_app.models import OfferDetail
from profile_app.models import BusinessProfile

User = get_user_model()

class OffersCreateTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Erstelle Business- und Customer-User
        cls.biz = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.biz, username='biz')  # type='business'
        cls.cust = User.objects.create_user(username='cust', password='pw')
        # URL
        cls.url = reverse('offer-list-create')

        cls.payload = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Paket.",
            "details": [
                {"title": "Basic", "revisions": 2, "delivery_time_in_days": 5, "price": 100, "features": ["A","B"], "offer_type": "basic"},
                {"title": "Std",   "revisions": 5, "delivery_time_in_days": 7, "price": 200, "features": ["A","B","C"], "offer_type": "standard"},
                {"title": "Prem",  "revisions":10, "delivery_time_in_days":10, "price": 500, "features": ["A","B","C","D"], "offer_type": "premium"},
            ]
        }

    def test_create_offer_success(self):
        self.client.force_authenticate(self.biz)
        resp = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', resp.data)
        self.assertEqual(len(resp.data['details']), 3)

    def test_create_offer_unauthenticated(self):
        resp = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_forbidden_for_customer(self):
        self.client.force_authenticate(self.cust)
        resp = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_invalid_details(self):
        self.client.force_authenticate(self.biz)
        bad_payload = self.payload.copy()
        bad_payload['details'] = []  # weniger als 3
        resp = self.client.post(self.url, bad_payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from offers_app.models import OfferDetail

User = get_user_model()


class OffersListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Erstelle zwei User und jeweils ein Offer mit Details
        cls.user1 = User.objects.create_user(username='biz1', password='pw')
        cls.user2 = User.objects.create_user(username='biz2', password='pw')
        # Angenommen BusinessProfile existiert und enforces creator rights – hier überspringen wir das
        offer1 = Offer.objects.create(user=cls.user1, title='Test Offer 1', description='Desc1')
        OfferDetail.objects.create(offer=offer1, title='D1', revisions=1, delivery_time_in_days=3, price=50, offer_type='basic')
        cls.url = reverse('offer-list-create')  # z.B. name='offers-list'

    def test_list_offers_no_auth(self):
        resp = self.client.get(self.url, {'page_size': 10})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        self.assertIsInstance(resp.data['results'], list)

    def test_filter_by_creator(self):
        resp = self.client.get(self.url, {'creator_id': self.user1.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertEqual(item['user'], self.user1.id)

    def test_search_and_ordering(self):
        # Suche nach Teilstring im Titel
        resp = self.client.get(self.url, {'search': 'Test', 'ordering': '-updated_at'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

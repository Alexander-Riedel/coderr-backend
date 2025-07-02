from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from offers_app.models import OfferDetail
from profile_app.models import BusinessProfile

User = get_user_model()


class OfferDetailObjectTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup Business-User + Offer + Detail
        cls.biz = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.biz, username='biz')
        cls.offer = Offer.objects.create(user=cls.biz, title='O', description='D')
        cls.detail = OfferDetail.objects.create(offer=cls.offer, title='Basic', revisions=1, delivery_time_in_days=5, price=100, offer_type='basic')
        cls.url = reverse('offerdetail-detail', kwargs={'pk': cls.detail.id})

    def test_get_offerdetail_success(self):
        self.client.force_authenticate(self.biz)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], self.detail.id)
        self.assertEqual(resp.data['offer_type'], 'basic')

    def test_get_offerdetail_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offerdetail_not_found(self):
        self.client.force_authenticate(self.biz)
        url = reverse('offerdetail-detail', kwargs={'pk': 9999})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

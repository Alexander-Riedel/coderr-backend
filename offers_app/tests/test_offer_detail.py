from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from offers_app.models import OfferDetail
from profile_app.models import BusinessProfile

User = get_user_model()


class OfferDetailTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Business-User und Profile
        cls.biz = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.biz, username='biz')
        # Ein Offer mit Details
        cls.offer = Offer.objects.create(user=cls.biz, title='O', description='D')
        cls.d1 = OfferDetail.objects.create(offer=cls.offer, title='X', revisions=1, delivery_time_in_days=5, price=50, offer_type='basic')
        cls.d2 = OfferDetail.objects.create(offer=cls.offer, title='Y', revisions=2, delivery_time_in_days=7, price=70, offer_type='standard')
        cls.url = reverse('offer-detail', kwargs={'pk': cls.offer.id})

        cls.other = User.objects.create_user(username='other', password='pw')

    def test_get_offer_success(self):
        self.client.force_authenticate(self.biz)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertEqual(data['id'], self.offer.id)
        self.assertEqual(data['min_price'], 50)
        self.assertEqual(data['min_delivery_time'], 5)
        self.assertEqual(len(data['details']), 2)

    def test_get_offer_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_not_found(self):
        self.client.force_authenticate(self.biz)
        url = reverse('offer-detail', kwargs={'pk': 9999})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_offer_success(self):
        self.client.force_authenticate(self.biz)
        payload = {"title": "Updated", "details": [{"id": self.d1.id, "title": "X+", "revisions":3, "delivery_time_in_days":6, "price":60, "features":["A"], "offer_type":"basic"}]}
        resp = self.client.patch(self.url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['title'], "Updated")

    def test_patch_offer_forbidden(self):
        self.client.force_authenticate(self.other)
        resp = self.client.patch(self.url, {"title":"Hack"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_success(self):
        self.client.force_authenticate(self.biz)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_forbidden(self):
        self.client.force_authenticate(self.other)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
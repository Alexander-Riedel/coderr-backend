# orders_app/tests/test_orders_create.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from offers_app.models import OfferDetail
from orders_app.models import Order
from profile_app.models import CustomerProfile, BusinessProfile

User = get_user_model()


class OrdersCreateTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Business und Customer anlegen
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')
        cls.customer = User.objects.create_user(username='cust', password='pw')
        CustomerProfile.objects.create(user=cls.customer, username='cust')
        # OfferDetail
        offer = Offer.objects.create(user=cls.business, title='O', description='D')
        cls.detail = OfferDetail.objects.create(
            offer=offer,
            title='Basic', revisions=1,
            delivery_time_in_days=5, price=100,
            offer_type='basic'
        )
        cls.url = reverse('order-list-create')
        cls.payload = {"offer_detail_id": cls.detail.id}

    def test_create_order_success(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['customer_user'], self.customer.id)

    def test_create_order_unauthenticated(self):
        resp = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_forbidden_for_business(self):
        self.client.force_authenticate(self.business)
        resp = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_invalid_payload(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.post(self.url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from orders_app.models import Order
from offers_app.models import Offer
from offers_app.models import OfferDetail
from profile_app.models import BusinessProfile, CustomerProfile

User = get_user_model()


class OrdersListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Users und Profile anlegen
        cls.customer = User.objects.create_user(username='cust', password='pw')
        CustomerProfile.objects.create(user=cls.customer, username='cust')
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')
        # OfferDetail und Order anlegen
        offer = Offer.objects.create(user=cls.business, title='O', description='D')
        detail = OfferDetail.objects.create(
            offer=offer,
            title='Basic', revisions=1,
            delivery_time_in_days=5, price=100,
            offer_type='basic'
        )
        # Bestellung
        cls.order = Order.objects.create(
            customer_user=cls.customer,
            business_user=cls.business,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
            status='in_progress'
        )
        cls.url = reverse('order-list-create')

    def test_list_orders_as_customer(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]['id'], self.order.id)

    def test_list_orders_as_business(self):
        self.client.force_authenticate(self.business)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]['business_user'], self.business.id)

    def test_list_orders_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

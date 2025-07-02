from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from orders_app.models import Order
from profile_app.models import BusinessProfile, CustomerProfile
from offers_app.models import Offer
from offers_app.models import OfferDetail

User = get_user_model()


class CompletedOrderCountTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')
        cls.customer = User.objects.create_user(username='cust', password='pw')
        CustomerProfile.objects.create(user=cls.customer, username='cust')
        # Offer & OfferDetail anlegen
        offer = Offer.objects.create(user=cls.business, title='O', description='D')
        detail = OfferDetail.objects.create(
            offer=offer,
            title='Basic', revisions=1,
            delivery_time_in_days=5, price=100,
            offer_type='basic'
        )
        # Completed Orders (ohne offer_detail-Feld)
        Order.objects.create(
            customer_user=cls.customer,
            business_user=cls.business,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
            status='completed'
        )
        Order.objects.create(
            customer_user=cls.customer,
            business_user=cls.business,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
            status='completed'
        )
        # One in_progress should be ignored
        Order.objects.create(
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

    def setUp(self):
        self.client.force_authenticate(self.business)
        self.url = reverse('completed-order-count', kwargs={'business_user_id': self.business.id})

    def test_get_completed_count(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['completed_order_count'], 2)

    def test_get_completed_unauthenticated(self):
        self.client.force_authenticate(None)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_completed_count_not_found(self):
        url = reverse('completed-order-count', kwargs={'business_user_id': 9999})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

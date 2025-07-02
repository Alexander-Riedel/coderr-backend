from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from orders_app.models import Order
from offers_app.models import Offer
from offers_app.models import OfferDetail
from profile_app.models import BusinessProfile, CustomerProfile

User = get_user_model()


class OrderDetailTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup Users & Profiles
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')
        cls.customer = User.objects.create_user(username='cust', password='pw')
        CustomerProfile.objects.create(user=cls.customer, username='cust')
        cls.other = User.objects.create_user(username='other', password='pw')
        # OfferDetail + Order
        offer = Offer.objects.create(user=cls.business, title='O', description='D')
        detail = OfferDetail.objects.create(
            offer=offer,
            title='Basic', revisions=1,
            delivery_time_in_days=5, price=100,
            offer_type='basic'
        )
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
        cls.url = reverse('order-detail', kwargs={'pk': cls.order.id})

    def test_get_order_success(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], self.order.id)

    def test_get_order_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_by_business(self):
        self.client.force_authenticate(self.business)
        resp = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'completed')

    def test_patch_order_forbidden_for_customer(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_by_staff(self):
        staff = User.objects.create_user(username='admin', password='pw', is_staff=True)
        self.client.force_authenticate(staff)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_delete_order_forbidden_for_nonstaff(self):
        self.client.force_authenticate(self.business)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

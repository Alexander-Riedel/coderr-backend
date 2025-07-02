from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from profile_app.models import CustomerProfile

User = get_user_model()


class CustomerProfilesListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='cust1', password='pw')
        cls.user2 = User.objects.create_user(username='cust2', password='pw')
        cls.business = User.objects.create_user(username='biz', password='pw')
        CustomerProfile.objects.create(user=cls.user1, username='cust1')
        CustomerProfile.objects.create(user=cls.user2, username='cust2')

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('customer-profile-list')

    def test_list_customer_authenticated(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        ids = [item['user'] for item in resp.data]
        self.assertIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)
        # Business-Nutzer nicht in Kunden-Liste
        self.assertNotIn(self.business.id, ids)

    def test_list_customer_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

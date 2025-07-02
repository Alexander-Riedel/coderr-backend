from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from profile_app.models import BusinessProfile

User = get_user_model()


class BusinessProfilesListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='biz1', password='pw')
        cls.user2 = User.objects.create_user(username='biz2', password='pw')
        cls.customer = User.objects.create_user(username='cust', password='pw')
        BusinessProfile.objects.create(user=cls.user1, username='biz1')
        BusinessProfile.objects.create(user=cls.user2, username='biz2')

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('business-profile-list')

    def test_list_business_authenticated(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        ids = [item['user'] for item in resp.data]
        self.assertIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)
        # Customer darf nicht in Business-Liste auftauchen
        self.assertNotIn(self.customer.id, ids)

    def test_list_business_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

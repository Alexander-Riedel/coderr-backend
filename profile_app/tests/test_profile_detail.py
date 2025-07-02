from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from profile_app.models import BusinessProfile, CustomerProfile

User = get_user_model()


class ProfileDetailTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.business_user = User.objects.create_user(
            username='bizuser', email='biz@example.com', password='pw123'
        )
        cls.customer_user = User.objects.create_user(
            username='custuser', email='cust@example.com', password='pw123'
        )
        # Profile anlegen
        BusinessProfile.objects.create(user=cls.business_user, username='bizuser')
        CustomerProfile.objects.create(user=cls.customer_user, username='custuser')
        cls.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pw123'
        )

    def setUp(self):
        self.client = APIClient()
        self.url_biz = reverse('user-profile-detail', kwargs={'pk': self.business_user.id})
        self.url_cust = reverse('user-profile-detail', kwargs={'pk': self.customer_user.id})

    def test_get_own_profile_success(self):
        self.client.force_authenticate(self.business_user)
        resp = self.client.get(self.url_biz)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertEqual(data['user'], self.business_user.id)
        self.assertEqual(data['username'], 'bizuser')
        self.assertEqual(data['email'], 'biz@example.com')
        self.assertEqual(data['type'], 'business')
        for f in ('first_name','last_name','location','tel','description','working_hours'):
            self.assertEqual(data[f], '')
        self.assertIn('created_at', data)

    def test_get_profile_unauthenticated(self):
        resp = self.client.get(self.url_biz)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        self.client.force_authenticate(self.business_user)
        url = reverse('user-profile-detail', kwargs={'pk': 999})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_success(self):
        self.client.force_authenticate(self.customer_user)
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "location": "Hamburg",
            "tel": "5551234",
            "description": "Neue Beschreibung",
            "working_hours": "8-16",
            "email": "new_cust@example.com"
        }
        resp = self.client.patch(self.url_cust, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['first_name'], "Jane")
        self.assertEqual(resp.data['email'], "new_cust@example.com")

    def test_patch_profile_forbidden(self):
        self.client.force_authenticate(self.other_user)
        resp = self.client.patch(self.url_biz, {"first_name": "Hack"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_unauthenticated(self):
        resp = self.client.patch(self.url_biz, {"first_name": "NoAuth"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

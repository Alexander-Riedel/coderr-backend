from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('registration')

    def test_registration_success(self):
        payload = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "secret123",
            "repeated_password": "secret123",
            "type": "customer"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], payload['username'])

    def test_registration_password_mismatch(self):
        payload = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "123",
            "repeated_password": "456",
            "type": "business"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# base_info_app/tests/test_base_info.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from profile_app.models import BusinessProfile
from reviews_app.models import Review
from offers_app.models import Offer

User = get_user_model()


class BaseInfoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 1) Zwei Business-User anlegen
        cls.user1 = User.objects.create_user(username='bus1', password='pw123')
        cls.user2 = User.objects.create_user(username='bus2', password='pw123')

        # 2) BusinessProfiles
        BusinessProfile.objects.create(user=cls.user1, username='B1')
        BusinessProfile.objects.create(user=cls.user2, username='B2')

        # 3) Reviews
        Review.objects.create(rating=5)
        Review.objects.create(rating=4)
        Review.objects.create(rating=3)

        # 4) Offers anlegen
        Offer.objects.create(user=cls.user1, title='O1')
        Offer.objects.create(user=cls.user1, title='O2')
        Offer.objects.create(user=cls.user2, title='O3')
        Offer.objects.create(user=cls.user2, title='O4')

    def setUp(self):
        self.url = reverse('base-info')

    def test_base_info_success(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data['review_count'], 3)
        self.assertAlmostEqual(data['average_rating'], 4.0, places=1)
        self.assertEqual(data['business_profile_count'], 2)
        self.assertEqual(data['offer_count'], 4)

    def test_wrong_method_not_allowed(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

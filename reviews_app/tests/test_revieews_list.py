from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from reviews_app.models import Review
from profile_app.models import BusinessProfile, CustomerProfile

User = get_user_model()


class ReviewsListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Business-User und zwei Reviewer anlegen
        cls.business = User.objects.create_user(username='biz', password='pw')
        BusinessProfile.objects.create(user=cls.business, username='biz')

        cls.reviewer1 = User.objects.create_user(username='rev1', password='pw')
        CustomerProfile.objects.create(user=cls.reviewer1, username='rev1')
        cls.reviewer2 = User.objects.create_user(username='rev2', password='pw')
        CustomerProfile.objects.create(user=cls.reviewer2, username='rev2')

        # Zwei Reviews für den gleichen Business-User
        cls.review1 = Review.objects.create(
            business_user=cls.business,
            reviewer=cls.reviewer1,
            rating=3,
            description='Okay Service'
        )
        cls.review2 = Review.objects.create(
            business_user=cls.business,
            reviewer=cls.reviewer2,
            rating=5,
            description='Top Service'
        )

        cls.url = reverse('review-list-create')  # z.B. name='reviews-list'

    def setUp(self):
        self.client = APIClient()

    def test_list_reviews_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_authenticated(self):
        self.client.force_authenticate(self.reviewer1)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        ids = [r['id'] for r in resp.data]
        self.assertIn(self.review1.id, ids)
        self.assertIn(self.review2.id, ids)

    def test_filter_by_business_user(self):
        self.client.force_authenticate(self.reviewer1)
        resp = self.client.get(self.url, {'business_user_id': self.business.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for r in resp.data:
            self.assertEqual(r['business_user'], self.business.id)

    def test_filter_by_reviewer(self):
        self.client.force_authenticate(self.reviewer1)
        resp = self.client.get(self.url, {'reviewer_id': self.reviewer1.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for r in resp.data:
            self.assertEqual(r['reviewer'], self.reviewer1.id)

    def test_ordering(self):
        self.client.force_authenticate(self.reviewer1)
        resp = self.client.get(self.url, {'ordering': '-rating'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ratings = [r['rating'] for r in resp.data]
        self.assertTrue(ratings[0] >= ratings[1])

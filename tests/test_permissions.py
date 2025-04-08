import pytest
from django.urls import reverse
from rest_framework import status
from datetime import datetime
from tests.factories import UserFactory, FoodFactory, MealFactory, HealthLogFactory, SleepFactory

pytestmark = pytest.mark.django_db

class TestAuthPermissions:
    def test_protected_endpoints_require_auth(self, api_client):
        """Test that protected endpoints return 401 without authentication"""
        protected_urls = [
            reverse('profile-detail'),
            reverse('food-list'),
            reverse('meal-list'),
            reverse('healthlog-list'),
            reverse('sleep-list'),
            reverse('analytics-health-trends'),
        ]
        
        for url in protected_urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestFoodPermissions:
    def test_private_food_access(self, authenticated_client, user):
        """Test that users can only access their private foods"""
        other_user = UserFactory.create()
        private_food = FoodFactory.create(user=other_user, is_public=False)
        
        url = reverse('food-detail', args=[private_food.id])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_public_food_access(self, authenticated_client):
        """Test that users can access public foods"""
        public_food = FoodFactory.create(is_public=True)
        
        url = reverse('food-detail', args=[public_food.id])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

class TestMealPermissions:
    def test_meal_access_restriction(self, authenticated_client):
        """Test that users can only access their own meals"""
        other_user = UserFactory.create()
        other_meal = MealFactory.create(user=other_user)
        
        url = reverse('meal-detail', args=[other_meal.id])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_meal_modification_restriction(self, authenticated_client):
        """Test that users can only modify their own meals"""
        other_user = UserFactory.create()
        other_meal = MealFactory.create(user=other_user)
        
        url = reverse('meal-detail', args=[other_meal.id])
        response = authenticated_client.put(url, {
            'date_time': '2024-04-08T12:00:00Z',
            'meal_type': 'lunch'
        })
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestHealthLogPermissions:
    def test_health_log_access_restriction(self, authenticated_client):
        """Test that users can only access their own health logs"""
        other_user = UserFactory.create()
        other_log = HealthLogFactory.create(user=other_user)
        
        url = reverse('healthlog-detail', args=[other_log.id])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_health_log_creation_restriction(self, authenticated_client, today):
        """Test that users can't create multiple health logs for the same day"""
        HealthLogFactory.create(user=authenticated_client.handler._force_user, date=today)
        
        url = reverse('healthlog-list')
        response = authenticated_client.post(url, {
            'date': today,
            'physical_feeling': 4,
            'mental_feeling': 4
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestSleepPermissions:
    def test_sleep_log_access_restriction(self, authenticated_client):
        """Test that users can only access their own sleep logs"""
        other_user = UserFactory.create()
        other_log = SleepFactory.create(user=other_user)
        
        url = reverse('sleep-detail', args=[other_log.id])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_sleep_log_creation_restriction(self, authenticated_client, today):
        """Test that users can't create multiple sleep logs for the same day"""
        SleepFactory.create(user=authenticated_client.handler._force_user, date=today)
        
        url = reverse('sleep-list')
        response = authenticated_client.post(url, {
            'date': today,
            'duration': '7.5',
            'quality': 4
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestAnalyticsPermissions:
    def test_analytics_access_restriction(self, api_client):
        """Test that analytics endpoints require authentication"""
        analytics_urls = [
            reverse('analytics-health-trends'),
            reverse('analytics-food-correlations'),
            reverse('analytics-sleep-analysis'),
            reverse('analytics-symptoms-triggers')
        ]
        
        for url in analytics_urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_medical_professional_access(self, authenticated_client, user):
        """Test that certain analytics are only available to medical professionals"""
        # Assuming there's an endpoint that requires medical professional status
        url = reverse('analytics-detailed-analysis')  # hypothetical endpoint
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        user.is_medical_professional = True
        user.save()
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

class TestRateLimiting:
    @pytest.mark.skip("Rate limiting disabled for tests")
    def test_api_rate_limiting(self, authenticated_client):
        """Test that rate limiting is enforced on API endpoints"""
        url = reverse('food-list')
        
        # Make multiple requests in quick succession
        for _ in range(100):
            response = authenticated_client.get(url)
        
        # The last request should be rate limited
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS 
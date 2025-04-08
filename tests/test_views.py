import pytest
from django.urls import reverse
from rest_framework import status
from datetime import timedelta

pytestmark = pytest.mark.django_db

class TestAuthViews:
    def test_user_registration(self, api_client):
        url = reverse('user-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data

    def test_user_login(self, api_client, user):
        url = reverse('token-obtain-pair')
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_account_update(self, authenticated_client, user):
        """Test that a user can update their account information"""
        url = reverse('user-detail')
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'height': '180.5',
            'phone': '555-123-4567'
        }
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'User'
        assert response.data['height'] == '180.50'
        assert response.data['phone'] == '555-123-4567'

    def test_user_account_deletion(self, authenticated_client, user):
        """Test that a user can delete their account"""
        url = reverse('user-delete')
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Try to login again - should fail
        login_url = reverse('token-obtain-pair')
        login_data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = authenticated_client.post(login_url, login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestProfileViews:
    def test_get_profile(self, authenticated_client, profile):
        url = reverse('profile-detail')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == profile.user.id

    def test_update_profile(self, authenticated_client, profile):
        url = reverse('profile-detail')
        data = {'medical_conditions': 'Updated conditions'}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['medical_conditions'] == 'Updated conditions'

class TestFoodViews:
    def test_list_foods(self, authenticated_client, food):
        url = reverse('food-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_food(self, authenticated_client):
        url = reverse('food-list')
        data = {
            'name': 'New Food',
            'calories': 200,
            'protein': '10.5',
            'carbs': '25.0',
            'fats': '8.5'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Food'

    def test_search_foods(self, authenticated_client, food):
        url = reverse('food-search')
        response = authenticated_client.get(url, {'query': food.name})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

class TestMealViews:
    def test_list_meals(self, authenticated_client, meal):
        url = reverse('meal-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_meal_with_foods(self, authenticated_client, food):
        url = reverse('meal-list')
        data = {
            'user': authenticated_client.handler._force_user.id,
            'date_time': '2024-04-08T12:00:00Z',
            'meal_type': 'lunch',
            'foods': [{'food_id': food.id, 'amount': 100}]
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['meal_type'] == 'lunch'

    def test_get_daily_meals(self, authenticated_client, meal, today):
        url = reverse('meal-daily', args=[today])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

class TestHealthLogViews:
    def test_list_health_logs(self, authenticated_client, health_log):
        url = reverse('healthlog-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_health_log(self, authenticated_client):
        url = reverse('healthlog-list')
        data = {
            'user': authenticated_client.handler._force_user.id,
            'date': '2024-04-08',
            'physical_feeling': 4,
            'mental_feeling': 4,
            'stool_count': 2,
            'stool_quality': 'normal',
            'complete_evacuation': True,
            'weight': '70.5'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['physical_feeling'] == 4

    def test_get_daily_health_log(self, authenticated_client, health_log, today):
        url = reverse('healthlog-daily', args=[today])
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == str(today)

class TestSleepViews:
    def test_list_sleep_logs(self, authenticated_client, sleep_log):
        url = reverse('sleep-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_sleep_log(self, authenticated_client):
        url = reverse('sleep-list')
        data = {
            'user': authenticated_client.handler._force_user.id,
            'date': '2024-04-08',
            'duration': '7.5',
            'quality': 4,
            'wake_up_ease': 3,
            'energy_level': 4
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['duration'] == '7.50'

class TestAnalyticsViews:
    def test_health_trends(self, authenticated_client, health_log):
        url = reverse('analytics-health-trends')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'physical_feeling' in response.data
        assert 'mental_feeling' in response.data

    def test_food_correlations(self, authenticated_client, meal_with_food, health_log):
        url = reverse('analytics-food-correlations')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_sleep_analysis(self, authenticated_client, sleep_log):
        url = reverse('analytics-sleep-analysis')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'average_duration' in response.data
        assert 'quality_trend' in response.data 

class TestExportViews:
    """Tests for data export functionality"""
    
    def test_export_health_data(self, authenticated_client, health_log):
        """Test exporting health log data to JSON"""
        url = reverse('export-health-data')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/json'
        
        # Check that the response contains data
        data = response.json()
        assert 'health_logs' in data
        assert isinstance(data['health_logs'], list)
        assert len(data['health_logs']) > 0
    
    def test_export_meal_data(self, authenticated_client, meal):
        """Test exporting meal data to JSON"""
        url = reverse('export-meal-data')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/json'
        
        # Check that the response contains data
        data = response.json()
        assert 'meals' in data
        assert isinstance(data['meals'], list)
        assert len(data['meals']) > 0
    
    def test_export_all_data(self, authenticated_client, meal, health_log, sleep_log):
        """Test exporting all user data to JSON"""
        url = reverse('export-all-data')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/json'
        
        # Check that the response contains all data types
        data = response.json()
        assert 'user' in data
        assert 'profile' in data
        assert 'meals' in data
        assert 'health_logs' in data
        assert 'sleep_logs' in data
        
        # Verify data is not empty
        assert len(data['meals']) > 0
        assert len(data['health_logs']) > 0
        assert len(data['sleep_logs']) > 0 
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from core.models import User, Profile, Food, Meal, MealFood, HealthLog, Sleep
from tests.factories import UserFactory

pytestmark = pytest.mark.django_db

class TestUserJourney:
    """
    Integration tests that follow a complete user journey through the system.
    These tests simulate real user interactions with the system.
    """
    
    def test_complete_daily_journey(self):
        """Test a complete daily user journey"""
        # 1. Create a new user and login
        client = APIClient()
        
        # Register a new user
        register_url = reverse('user-register')
        register_data = {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = client.post(register_url, register_data)
        assert response.status_code == status.HTTP_201_CREATED
        user_id = response.data['id']
        token = response.data['token']
        
        # Set authentication
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 2. Complete profile
        profile_url = reverse('profile-detail')
        profile_data = {
            'medical_conditions': 'IBS',
            'allergies': 'Lactose intolerance',
            'dietary_restrictions': 'Low FODMAP',
            'goals': 'Improve digestive health'
        }
        response = client.patch(profile_url, profile_data)
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Add custom foods
        food_url = reverse('food-list')
        foods = [
            {
                'name': 'Gluten-free Bread',
                'calories': 220,
                'protein': '5.0',
                'carbs': '45.0',
                'fats': '2.5',
                'is_public': True
            },
            {
                'name': 'Lactose-free Yogurt',
                'calories': 150,
                'protein': '12.0',
                'carbs': '15.0',
                'fats': '4.5',
                'is_public': True
            }
        ]
        
        for food_data in foods:
            response = client.post(food_url, food_data)
            assert response.status_code == status.HTTP_201_CREATED
        
        # 4. Log breakfast meal
        meal_url = reverse('meal-list')
        breakfast_data = {
            'user': user_id,
            'date_time': f"{timezone.now().isoformat()}",
            'meal_type': 'breakfast',
            'notes': 'Morning breakfast',
            'foods': [
                {
                    'food_id': 1,
                    'amount': 100,
                    'notes': 'Two slices'
                },
                {
                    'food_id': 2,
                    'amount': 150,
                    'notes': 'One cup'
                }
            ]
        }
        response = client.post(meal_url, breakfast_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # 5. Log health data for the day
        health_url = reverse('healthlog-list')
        health_data = {
            'user': user_id,
            'date': timezone.now().date().isoformat(),
            'physical_feeling': 4,
            'mental_feeling': 4,
            'stool_count': 1,
            'stool_quality': 'normal',
            'complete_evacuation': True,
            'weight': '70.5',
            'symptoms': 'Slight bloating after lunch',
            'notes': 'Overall good day'
        }
        response = client.post(health_url, health_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # 6. Log sleep data
        sleep_url = reverse('sleep-list')
        sleep_data = {
            'user': user_id,
            'date': timezone.now().date().isoformat(),
            'duration': '7.5',
            'quality': 4,
            'wake_up_ease': 3,
            'energy_level': 4,
            'notes': 'Slept well, woke up once'
        }
        response = client.post(sleep_url, sleep_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # 7. View daily summary
        day = timezone.now().date().isoformat()
        meals_url = reverse('meal-daily', args=[day])
        response = client.get(meals_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # One meal logged
        
        health_url = reverse('healthlog-daily', args=[day])
        response = client.get(health_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['physical_feeling'] == 4
        
        # 8. Check analytics
        analytics_url = reverse('analytics-health-trends')
        response = client.get(analytics_url)
        assert response.status_code == status.HTTP_200_OK
        assert 'physical_feeling' in response.data
        
        # 9. Export data
        export_url = reverse('export-all-data')
        response = client.get(export_url)
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'meals' in response.data
        assert 'health_logs' in response.data
        assert 'sleep_logs' in response.data

    def test_weekly_analysis_journey(self):
        """Test a user journey focused on weekly analysis"""
        # 1. Create a user with a week of data
        user = UserFactory.create()
        client = APIClient()
        
        # Get a token for the user
        token_url = reverse('token-obtain-pair')
        response = client.post(token_url, {
            'username': user.username,
            'password': 'testpass123'  # Default from factory
        })
        assert response.status_code == status.HTTP_200_OK
        token = response.data['access']
        
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 2. Create a week of data
        today = timezone.now().date()
        
        # Create foods
        food1 = Food.objects.create(
            name='Oatmeal',
            calories=150,
            protein=Decimal('5.0'),
            carbs=Decimal('27.0'),
            fats=Decimal('2.5'),
            user=user
        )
        
        food2 = Food.objects.create(
            name='Chicken Salad',
            calories=350,
            protein=Decimal('30.0'),
            carbs=Decimal('10.0'),
            fats=Decimal('20.0'),
            user=user
        )
        
        # Create a week of meals, health logs and sleep logs
        for i in range(7):
            day = today - timedelta(days=i)
            
            # Create breakfast
            breakfast = Meal.objects.create(
                user=user,
                date_time=timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()) + timedelta(hours=8)),
                meal_type='breakfast',
                notes=f'Breakfast for day {i+1}'
            )
            MealFood.objects.create(
                meal=breakfast,
                food=food1,
                amount=Decimal('100.0')
            )
            
            # Create lunch
            lunch = Meal.objects.create(
                user=user,
                date_time=timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()) + timedelta(hours=13)),
                meal_type='lunch',
                notes=f'Lunch for day {i+1}'
            )
            MealFood.objects.create(
                meal=lunch,
                food=food2,
                amount=Decimal('200.0')
            )
            
            # Create health log
            HealthLog.objects.create(
                user=user,
                date=day,
                physical_feeling=4 if i % 2 == 0 else 3,
                mental_feeling=4 if i % 3 == 0 else 3,
                stool_count=i % 3 + 1,
                stool_quality='normal' if i % 2 == 0 else 'soft',
                complete_evacuation=i % 2 == 0,
                weight=Decimal('70.0') + (Decimal('0.1') * i),
                symptoms='None' if i % 2 == 0 else 'Slight bloating',
                notes=f'Health log for day {i+1}'
            )
            
            # Create sleep log
            Sleep.objects.create(
                user=user,
                date=day,
                duration=Decimal('7.5') - (Decimal('0.2') * (i % 3)),
                quality=4 if i % 2 == 0 else 3,
                wake_up_ease=3,
                energy_level=4 if i % 2 == 0 else 3,
                notes=f'Sleep log for day {i+1}'
            )
        
        # 3. View weekly summary
        weekly_date = today.isoformat()
        meals_url = reverse('meal-weekly', args=[weekly_date])
        response = client.get(meals_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Expecting only meals from TODAY and forward
        # Each day has 2 meals, so today should have 2 meals
        assert len(response.data) == 2
        
        # 4. Check analytics
        analytics_url = reverse('analytics-health-trends')
        response = client.get(analytics_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['physical_feeling']) == 7
        
        sleep_analysis_url = reverse('analytics-sleep-analysis')
        response = client.get(sleep_analysis_url)
        assert response.status_code == status.HTTP_200_OK
        assert 'average_duration' in response.data
        assert len(response.data['quality_trend']) == 7
        
        food_correlations_url = reverse('analytics-food-correlations')
        response = client.get(food_correlations_url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0 
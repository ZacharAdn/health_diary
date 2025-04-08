import pytest
from django.utils import timezone
from core.serializers import (
    UserSerializer,
    ProfileSerializer,
    FoodSerializer,
    MealSerializer,
    MealFoodSerializer,
    HealthLogSerializer,
    SleepSerializer
)

pytestmark = pytest.mark.django_db

class TestUserSerializer:
    def test_serialize_user(self, user):
        serializer = UserSerializer(user)
        assert serializer.data['username'] == user.username
        assert serializer.data['email'] == user.email
        assert 'password' not in serializer.data

    def test_deserialize_user(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == 'newuser'
        assert user.check_password('testpass123')

class TestProfileSerializer:
    def test_serialize_profile(self, profile):
        serializer = ProfileSerializer(profile)
        assert serializer.data['user'] == profile.user.id
        assert serializer.data['medical_conditions'] == profile.medical_conditions
        assert serializer.data['allergies'] == profile.allergies

    def test_deserialize_profile(self, user):
        data = {
            'user': user.id,
            'medical_conditions': 'Test condition',
            'allergies': 'Test allergy',
            'dietary_restrictions': 'No gluten',
            'goals': 'Weight loss'
        }
        serializer = ProfileSerializer(data=data)
        assert serializer.is_valid()
        profile = serializer.save()
        assert profile.medical_conditions == 'Test condition'

class TestFoodSerializer:
    def test_serialize_food(self, food):
        serializer = FoodSerializer(food)
        assert serializer.data['name'] == food.name
        assert serializer.data['calories'] == food.calories
        assert float(serializer.data['protein']) == float(food.protein)

    def test_deserialize_food(self):
        data = {
            'name': 'Test Food',
            'calories': 200,
            'protein': '10.5',
            'carbs': '25.0',
            'fats': '8.5',
            'is_public': True
        }
        serializer = FoodSerializer(data=data)
        assert serializer.is_valid()
        food = serializer.save()
        assert food.name == 'Test Food'
        assert food.calories == 200

class TestMealSerializer:
    def test_serialize_meal(self, meal):
        serializer = MealSerializer(meal)
        assert serializer.data['meal_type'] == meal.meal_type
        assert serializer.data['user'] == meal.user.id

    def test_deserialize_meal_with_foods(self, user, food):
        data = {
            'user': user.id,
            'date_time': '2024-04-08T12:00:00Z',
            'meal_type': 'lunch',
            'notes': 'Test meal',
            'foods': [{'food_id': food.id, 'amount': 100}]
        }
        serializer = MealSerializer(data=data)
        assert serializer.is_valid()
        meal = serializer.save()
        assert meal.meal_type == 'lunch'
        assert meal.mealfood_set.count() == 1

class TestHealthLogSerializer:
    def test_serialize_health_log(self, health_log):
        serializer = HealthLogSerializer(health_log)
        assert serializer.data['physical_feeling'] == health_log.physical_feeling
        assert serializer.data['mental_feeling'] == health_log.mental_feeling
        assert serializer.data['stool_quality'] == health_log.stool_quality

    def test_deserialize_health_log(self, user):
        data = {
            'user': user.id,
            'date': '2024-04-08',
            'physical_feeling': 4,
            'mental_feeling': 4,
            'stool_count': 2,
            'stool_quality': 'normal',
            'complete_evacuation': True,
            'weight': '70.5',
            'symptoms': 'None',
            'notes': 'Good day'
        }
        serializer = HealthLogSerializer(data=data)
        assert serializer.is_valid()
        health_log = serializer.save()
        assert health_log.physical_feeling == 4
        assert health_log.stool_quality == 'normal'

class TestSleepSerializer:
    def test_serialize_sleep(self, sleep_log):
        serializer = SleepSerializer(sleep_log)
        assert float(serializer.data['duration']) == float(sleep_log.duration)
        assert serializer.data['quality'] == sleep_log.quality
        assert serializer.data['wake_up_ease'] == sleep_log.wake_up_ease

    def test_deserialize_sleep(self, user):
        data = {
            'user': user.id,
            'date': '2024-04-08',
            'duration': '7.5',
            'quality': 4,
            'wake_up_ease': 3,
            'energy_level': 4,
            'notes': 'Good sleep'
        }
        serializer = SleepSerializer(data=data)
        assert serializer.is_valid()
        sleep = serializer.save()
        assert float(sleep.duration) == 7.5
        assert sleep.quality == 4

    def test_validate_metrics_range(self):
        data = {
            'user': 1,
            'date': '2024-04-08',
            'duration': '7.5',
            'quality': 6,  # Invalid value
            'wake_up_ease': 3,
            'energy_level': 4
        }
        serializer = SleepSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quality' in serializer.errors 
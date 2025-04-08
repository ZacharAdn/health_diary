import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal
from tests.factories import UserFactory, ProfileFactory, FoodFactory, MealFactory, MealFoodFactory, HealthLogFactory, SleepFactory

pytestmark = pytest.mark.django_db

class TestUserModel:
    def test_user_creation(self, user):
        assert user.username
        assert user.email
        assert user.is_active
        assert not user.is_medical_professional

    def test_user_email_unique(self, user):
        with pytest.raises(IntegrityError):
            UserFactory.create(email=user.email)

class TestProfileModel:
    def test_profile_creation(self, profile):
        assert profile.user
        assert isinstance(profile.medical_conditions, str)
        assert isinstance(profile.allergies, str)
        assert isinstance(profile.dietary_restrictions, str)
        assert isinstance(profile.goals, str)

    def test_profile_user_one_to_one(self, user):
        profile1 = ProfileFactory.create(user=user)
        with pytest.raises(IntegrityError):
            ProfileFactory.create(user=user)

class TestFoodModel:
    def test_food_creation(self, food):
        assert food.name
        assert isinstance(food.calories, int)
        assert isinstance(food.protein, Decimal)
        assert isinstance(food.carbs, Decimal)
        assert isinstance(food.fats, Decimal)
        assert food.is_public

    def test_food_macros_validation(self):
        with pytest.raises(ValidationError):
            food = FoodFactory.build(protein=Decimal('-1.0'))
            food.full_clean()

class TestMealModel:
    def test_meal_creation(self, meal):
        assert meal.user
        assert meal.date_time
        assert meal.meal_type in ['breakfast', 'lunch', 'dinner', 'snack']
        assert isinstance(meal.notes, str)

    def test_meal_type_validation(self):
        with pytest.raises(ValidationError):
            meal = MealFactory.build(meal_type='invalid')
            meal.full_clean()

class TestMealFoodModel:
    def test_meal_food_creation(self, meal_with_food):
        meal_food = meal_with_food.mealfood_set.first()
        assert meal_food.meal == meal_with_food
        assert meal_food.food
        assert meal_food.amount > 0
        assert isinstance(meal_food.notes, str)

    def test_meal_food_amount_validation(self):
        with pytest.raises(ValidationError):
            meal_food = MealFoodFactory.build(amount=0)
            meal_food.full_clean()

class TestHealthLogModel:
    def test_health_log_creation(self, health_log):
        assert health_log.user
        assert health_log.date
        assert 1 <= health_log.physical_feeling <= 5
        assert 1 <= health_log.mental_feeling <= 5
        assert health_log.stool_count >= 0
        assert health_log.stool_quality in ['hard', 'normal', 'soft', 'diarrhea']
        assert isinstance(health_log.complete_evacuation, bool)
        assert isinstance(health_log.weight, Decimal)
        assert isinstance(health_log.symptoms, str)
        assert isinstance(health_log.notes, str)

    def test_health_log_feeling_validation(self):
        with pytest.raises(ValidationError):
            health_log = HealthLogFactory.build(physical_feeling=6)
            health_log.full_clean()

        with pytest.raises(ValidationError):
            health_log = HealthLogFactory.build(mental_feeling=0)
            health_log.full_clean()

class TestSleepModel:
    def test_sleep_creation(self, sleep_log):
        assert sleep_log.user
        assert sleep_log.date
        assert isinstance(sleep_log.duration, Decimal)
        assert 1 <= sleep_log.quality <= 5
        assert 1 <= sleep_log.wake_up_ease <= 5
        assert 1 <= sleep_log.energy_level <= 5
        assert isinstance(sleep_log.notes, str)

    def test_sleep_metrics_validation(self):
        with pytest.raises(ValidationError):
            sleep = SleepFactory.build(quality=6)
            sleep.full_clean()

        with pytest.raises(ValidationError):
            sleep = SleepFactory.build(wake_up_ease=0)
            sleep.full_clean()

        with pytest.raises(ValidationError):
            sleep = SleepFactory.build(energy_level=6)
            sleep.full_clean() 
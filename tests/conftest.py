import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import datetime, timedelta

from .factories import (
    UserFactory, 
    ProfileFactory, 
    FoodFactory, 
    MealFactory, 
    MealFoodFactory,
    HealthLogFactory,
    SleepFactory
)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory.create()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def profile(user):
    return ProfileFactory.create(user=user)

@pytest.fixture
def food():
    return FoodFactory.create()

@pytest.fixture
def meal(user):
    return MealFactory.create(user=user)

@pytest.fixture
def meal_with_food(meal, food):
    MealFoodFactory.create(meal=meal, food=food, amount=100)
    return meal

@pytest.fixture
def health_log(user):
    return HealthLogFactory.create(user=user)

@pytest.fixture
def sleep_log(user):
    return SleepFactory.create(user=user)

@pytest.fixture
def today():
    return timezone.now().date()

@pytest.fixture
def yesterday():
    return timezone.now().date() - timedelta(days=1)

@pytest.fixture
def tomorrow():
    return timezone.now().date() + timedelta(days=1) 
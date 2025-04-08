import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import time
from django.contrib.auth import get_user_model
from core.models import Profile, Food, Meal, MealFood, HealthLog, Sleep

class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True

class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    medical_conditions = factory.Faker('text', max_nb_chars=200)
    allergies = factory.Faker('text', max_nb_chars=100)
    dietary_restrictions = factory.Faker('text', max_nb_chars=100)
    goals = factory.Faker('text', max_nb_chars=200)

class FoodFactory(DjangoModelFactory):
    class Meta:
        model = Food

    name = factory.Sequence(lambda n: f"Food Item {n}")
    calories = factory.Faker('random_int', min=50, max=1000)
    protein = factory.Faker('pydecimal', min_value=0, max_value=100, right_digits=2)
    carbs = factory.Faker('pydecimal', min_value=0, max_value=100, right_digits=2)
    fats = factory.Faker('pydecimal', min_value=0, max_value=100, right_digits=2)
    is_public = True

class MealFactory(DjangoModelFactory):
    class Meta:
        model = Meal

    user = factory.SubFactory(UserFactory)
    date_time = factory.LazyFunction(timezone.now)
    meal_type = factory.Iterator(['breakfast', 'lunch', 'dinner', 'snack'])
    notes = factory.Faker('text', max_nb_chars=200)

class MealFoodFactory(DjangoModelFactory):
    class Meta:
        model = MealFood

    meal = factory.SubFactory(MealFactory)
    food = factory.SubFactory(FoodFactory)
    amount = factory.Faker('random_int', min=10, max=1000)
    notes = factory.Faker('text', max_nb_chars=100)

class HealthLogFactory(DjangoModelFactory):
    class Meta:
        model = HealthLog

    user = factory.SubFactory(UserFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())
    physical_feeling = factory.Faker('random_int', min=1, max=5)
    mental_feeling = factory.Faker('random_int', min=1, max=5)
    stool_count = factory.Faker('random_int', min=0, max=5)
    stool_quality = factory.Iterator(['hard', 'normal', 'soft', 'diarrhea'])
    complete_evacuation = factory.Faker('boolean')
    weight = factory.Faker('pydecimal', min_value=40, max_value=150, right_digits=2)
    symptoms = factory.Faker('text', max_nb_chars=200)
    notes = factory.Faker('text', max_nb_chars=200)

class SleepFactory(DjangoModelFactory):
    class Meta:
        model = Sleep

    user = factory.SubFactory(UserFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())
    duration = factory.Faker('pydecimal', min_value=4, max_value=12, right_digits=2)
    quality = factory.Faker('random_int', min=1, max=5)
    wake_up_ease = factory.Faker('random_int', min=1, max=5)
    energy_level = factory.Faker('random_int', min=1, max=5)
    notes = factory.Faker('text', max_nb_chars=200) 
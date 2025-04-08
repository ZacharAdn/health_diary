import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from core.models import User, Profile, Food, Meal, MealFood, HealthLog, Sleep
from core.services import HealthAnalyticsService
from tests.factories import (
    UserFactory, FoodFactory, MealFactory, MealFoodFactory,
    HealthLogFactory, SleepFactory
)

pytestmark = pytest.mark.django_db

class TestHealthAnalyticsService:
    def test_get_health_trends(self, db):
        """Test retrieving health trends for a user over time"""
        # Create a user
        user = UserFactory.create()
        
        # Create health logs for the past 7 days
        today = timezone.now().date()
        for i in range(7):
            day = today - timedelta(days=i)
            HealthLogFactory.create(
                user=user,
                date=day,
                physical_feeling=3 + (i % 3),  # Values between 3-5
                mental_feeling=3 + (i % 3),  # Values between 3-5
                stool_quality='normal' if i % 2 == 0 else 'soft',
                weight=Decimal('70.5') + Decimal(i) * Decimal('0.1')  # Slight increase each day
            )
        
        # Get trends for last 7 days
        trends = HealthAnalyticsService.get_health_trends(user, days=7)
        
        # Verify results
        assert 'physical_feeling' in trends
        assert 'mental_feeling' in trends
        assert 'stool_quality' in trends
        assert 'weight' in trends
        
        # Should have 7 days of data
        assert len(trends['physical_feeling']) == 7
        assert len(trends['mental_feeling']) == 7
        assert len(trends['stool_quality']) == 7
        assert len(trends['weight']) == 7
        
        # Verify data format
        for item in trends['physical_feeling']:
            assert 'date' in item
            assert 'value' in item
            assert isinstance(item['value'], int)
            assert 1 <= item['value'] <= 5
    
    def test_get_food_correlations(self, db):
        """Test correlating foods with health metrics"""
        # Create a user
        user = UserFactory.create()
        today = timezone.now().date()
        
        # Create food items
        food1 = FoodFactory.create(name="Milk", user=user)
        food2 = FoodFactory.create(name="Bread", user=user)
        food3 = FoodFactory.create(name="Spicy Food", user=user)
        
        # Create meals and health logs spanning 5 days
        for i in range(5):
            day = today - timedelta(days=i)
            
            # Create a meal for this day
            meal = MealFactory.create(
                user=user,
                date_time=timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
            )
            
            # Add foods to the meal
            if i % 2 == 0:  # On even days, eat spicy food (potential trigger)
                MealFoodFactory.create(meal=meal, food=food3, amount=100)
            else:
                MealFoodFactory.create(meal=meal, food=food1, amount=200)
                MealFoodFactory.create(meal=meal, food=food2, amount=150)
            
            # Create health log for the next day
            if i < 4:  # We don't need health log for the last day
                next_day = day - timedelta(days=1)
                # Physical feeling worse after spicy food days
                physical_feeling = 2 if (i % 2 == 0) else 4
                HealthLogFactory.create(
                    user=user,
                    date=next_day,
                    physical_feeling=physical_feeling,
                    mental_feeling=3,
                    stool_quality='soft' if (i % 2 == 0) else 'normal'
                )
        
        # Get food correlations
        correlations = HealthAnalyticsService.get_food_correlations(user, days=5)
        
        # Verify results
        assert isinstance(correlations, list)
        assert len(correlations) > 0
        
        # Verify data structure
        for item in correlations:
            assert 'date' in item
            assert 'physical_feeling' in item
            assert 'mental_feeling' in item
            assert 'foods_eaten_same_day' in item
            assert 'foods_eaten_previous_day' in item
    
    def test_analyze_sleep(self, db):
        """Test sleep pattern analysis"""
        # Create a user
        user = UserFactory.create()
        today = timezone.now().date()
        
        # Create sleep logs for the past 10 days
        for i in range(10):
            day = today - timedelta(days=i)
            SleepFactory.create(
                user=user,
                date=day,
                duration=Decimal('7.5') - (Decimal('0.2') * (i % 3)),  # Vary between 7.1-7.5
                quality=4 if i % 2 == 0 else 3,  # Alternate between 3 and 4
                wake_up_ease=3,
                energy_level=3 if i % 2 == 0 else 4  # Alternate between 3 and 4
            )
        
        # Analyze sleep for last 7 days
        analysis = HealthAnalyticsService.analyze_sleep(user, days=7)
        
        # Verify results
        assert 'average_duration' in analysis
        assert 'average_quality' in analysis
        assert 'average_energy' in analysis
        assert 'quality_trend' in analysis
        assert 'duration_trend' in analysis
        
        # Should have 7 days of data in trends
        assert len(analysis['quality_trend']) == 7
        assert len(analysis['duration_trend']) == 7
        
        # Average values should be reasonable
        assert 6 <= float(analysis['average_duration']) <= 8
        assert 1 <= float(analysis['average_quality']) <= 5
        assert 1 <= float(analysis['average_energy']) <= 5
    
    def test_identify_symptom_triggers(self, db):
        """Test identifying foods that may trigger symptoms"""
        # Create a user
        user = UserFactory.create()
        today = timezone.now().date()
        
        # Create common foods
        food1 = FoodFactory.create(name="Dairy", user=user)
        food2 = FoodFactory.create(name="Gluten", user=user)
        food3 = FoodFactory.create(name="Vegetables", user=user)
        food4 = FoodFactory.create(name="Fruit", user=user)
        
        # Create meals and health logs spanning 20 days
        for i in range(20):
            day = today - timedelta(days=i)
            
            # Create a meal for this day
            meal = MealFactory.create(
                user=user,
                date_time=timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
            )
            
            # Add foods to the meal - make dairy appear more often before poor health days
            MealFoodFactory.create(meal=meal, food=food1, amount=100 if i % 3 == 0 else 0)
            MealFoodFactory.create(meal=meal, food=food2, amount=100 if i % 4 == 0 else 0)
            MealFoodFactory.create(meal=meal, food=food3, amount=100)  # Always eat vegetables
            MealFoodFactory.create(meal=meal, food=food4, amount=100 if i % 2 == 0 else 0)
            
            # Create health log for the next day
            if i < 19:  # We don't need health log for the last day
                next_day = day - timedelta(days=1)
                # Physical feeling worse after dairy days
                physical_feeling = 2 if (i % 3 == 0) else 4
                HealthLogFactory.create(
                    user=user,
                    date=next_day,
                    physical_feeling=physical_feeling,
                    mental_feeling=3,
                    stool_quality='soft' if (i % 3 == 0) else 'normal'
                )
        
        # Identify symptom triggers
        triggers = HealthAnalyticsService.identify_symptom_triggers(user, days=20)
        
        # Verify results
        assert isinstance(triggers, list)
        assert len(triggers) > 0
        
        # Dairy should be one of the top triggers
        found_dairy = False
        for trigger in triggers:
            if trigger['food'] == 'Dairy':
                found_dairy = True
                break
        
        assert found_dairy, "Dairy should be identified as a trigger food"
        
        # Verify data structure
        for trigger in triggers:
            assert 'food' in trigger
            assert 'count' in trigger
            assert isinstance(trigger['count'], int)
    
    def test_time_range_filtering(self, db):
        """Test that services properly filter data by time range"""
        # Create a user
        user = UserFactory.create()
        today = timezone.now().date()
        
        # Create health logs spanning 60 days
        for i in range(60):
            day = today - timedelta(days=i)
            HealthLogFactory.create(
                user=user,
                date=day,
                physical_feeling=3,
                mental_feeling=3
            )
        
        # Get trends with different time ranges
        trends_7 = HealthAnalyticsService.get_health_trends(user, days=7)
        trends_30 = HealthAnalyticsService.get_health_trends(user, days=30)
        trends_60 = HealthAnalyticsService.get_health_trends(user, days=60)
        
        # Verify that the number of data points matches the time range
        assert len(trends_7['physical_feeling']) == 7
        assert len(trends_30['physical_feeling']) == 30
        assert len(trends_60['physical_feeling']) == 60 
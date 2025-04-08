from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from .models import HealthLog, Meal, MealFood, Sleep, Food

class HealthAnalyticsService:
    """Service for health analytics and insights"""
    
    @staticmethod
    def get_health_trends(user, days=30):
        """Get health trends over the last n days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)  # -1 because end_date is inclusive
        
        health_logs = HealthLog.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')[:days]  # Limit to exactly 'days' number of records
        
        # Convert to list and sort by date for consistent processing
        health_logs = sorted(list(health_logs), key=lambda log: log.date)
        
        # Convert date objects to strings for JSON serialization
        return {
            'physical_feeling': [
                {'date': str(log.date), 'value': log.physical_feeling} 
                for log in health_logs
            ],
            'mental_feeling': [
                {'date': str(log.date), 'value': log.mental_feeling} 
                for log in health_logs
            ],
            'stool_quality': [
                {'date': str(log.date), 'value': log.stool_quality} 
                for log in health_logs if log.stool_quality
            ],
            'weight': [
                {'date': str(log.date), 'value': float(log.weight) if log.weight else None} 
                for log in health_logs if log.weight
            ],
        }
    
    @staticmethod
    def get_food_correlations(user, days=30):
        """Analyze correlation between foods and health metrics"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get health logs for date range
        health_logs = HealthLog.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Get meals from date range
        meals = Meal.objects.filter(
            user=user,
            date_time__date__gte=start_date,
            date_time__date__lte=end_date
        ).prefetch_related('mealfood_set__food')
        
        # Build a map of date -> foods eaten
        date_to_foods = defaultdict(list)
        for meal in meals:
            meal_date = meal.date_time.date()
            for meal_food in meal.mealfood_set.all():
                date_to_foods[meal_date].append({
                    'name': meal_food.food.name,
                    'amount': str(meal_food.amount)
                })
        
        # Combine health metrics with foods eaten
        correlations = []
        for log in health_logs:
            # Get foods from same day
            foods_eaten = date_to_foods.get(log.date, [])
            
            # Get foods from previous day that may affect today's health
            prev_day_foods = date_to_foods.get(log.date - timedelta(days=1), [])
            
            correlations.append({
                'date': str(log.date),
                'physical_feeling': log.physical_feeling,
                'mental_feeling': log.mental_feeling,
                'stool_quality': log.stool_quality,
                'foods_eaten_same_day': foods_eaten,
                'foods_eaten_previous_day': prev_day_foods
            })
        
        return correlations
    
    @staticmethod
    def analyze_sleep(user, days=30):
        """Analyze sleep patterns"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)  # -1 because end_date is inclusive
        
        sleep_logs = Sleep.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')[:days]  # Limit to exactly 'days' number of records
        
        # Convert to list and sort by date for consistent processing
        sleep_logs = sorted(list(sleep_logs), key=lambda log: log.date)
        
        # Calculate averages
        if sleep_logs:
            avg_duration = sum(float(log.duration) for log in sleep_logs) / len(sleep_logs)
            avg_quality = sum(log.quality for log in sleep_logs) / len(sleep_logs)
            avg_energy = sum(log.energy_level for log in sleep_logs) / len(sleep_logs)
        else:
            avg_duration = avg_quality = avg_energy = 0
        
        # Generate trends data
        quality_trend = [
            {'date': str(log.date), 'value': log.quality} 
            for log in sleep_logs
        ]
        
        duration_trend = [
            {'date': str(log.date), 'value': float(log.duration)} 
            for log in sleep_logs
        ]
        
        return {
            'average_duration': avg_duration,
            'average_quality': avg_quality,
            'average_energy': avg_energy,
            'quality_trend': quality_trend,
            'duration_trend': duration_trend
        }
    
    @staticmethod
    def identify_symptom_triggers(user, days=60):
        """Identify potential food triggers for symptoms"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get health logs where physical_feeling is low (1-2)
        poor_health_days = HealthLog.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date,
            physical_feeling__lte=2
        ).values_list('date', flat=True)
        
        # Convert QuerySet to list for debugging
        poor_health_days = list(poor_health_days)
        
        # Log for debugging
        print(f"Found {len(poor_health_days)} poor health days")
        
        # Get one day before each poor health day
        potential_trigger_days = [day - timedelta(days=1) for day in poor_health_days]
        
        # Get foods eaten on potential trigger days
        potential_triggers = {}
        for trigger_day in potential_trigger_days:
            meals = Meal.objects.filter(
                user=user,
                date_time__date=trigger_day
            ).prefetch_related('mealfood_set__food')
            
            for meal in meals:
                for meal_food in meal.mealfood_set.all():
                    food_name = meal_food.food.name
                    if food_name in potential_triggers:
                        potential_triggers[food_name] += 1
                    else:
                        potential_triggers[food_name] = 1
        
        # Sort by frequency
        sorted_triggers = sorted(
            [{'food': k, 'count': v} for k, v in potential_triggers.items()],
            key=lambda x: x['count'],
            reverse=True
        )
        
        return sorted_triggers[:10]  # Return top 10 potential triggers 
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, datetime
import random
from decimal import Decimal

from tests.factories import (
    UserFactory, 
    ProfileFactory, 
    FoodFactory, 
    MealFactory, 
    MealFoodFactory,
    HealthLogFactory,
    SleepFactory
)

class Command(BaseCommand):
    help = 'Populates the database with fake data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--days', type=int, default=30, help='Number of days of data to generate')
        parser.add_argument('--food_items', type=int, default=50, help='Number of food items to create')
        parser.add_argument('--public_ratio', type=float, default=0.7, help='Ratio of food items that are public')
        parser.add_argument('--admin', action='store_true', help='Create a superuser admin@example.com with password "admin123"')
    
    def handle(self, *args, **options):
        user_count = options['users']
        days_of_data = options['days']
        food_items_count = options['food_items']
        public_ratio = options['public_ratio']
        create_admin = options['admin']
        
        self.stdout.write(self.style.SUCCESS(f'Starting to populate database with fake data...'))
        
        try:
            with transaction.atomic():
                # Create an admin user if requested
                if create_admin:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    
                    if not User.objects.filter(username='admin').exists():
                        admin_user = User.objects.create_superuser(
                            username='admin',
                            email='admin@example.com',
                            password='admin123'
                        )
                        self.stdout.write(self.style.SUCCESS(f'Created admin user: admin@example.com / admin123'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Admin user already exists'))
                
                # Create regular users with profiles
                self.stdout.write(self.style.SUCCESS(f'Creating {user_count} users with profiles...'))
                users = []
                for i in range(user_count):
                    user = UserFactory()
                    ProfileFactory(user=user)
                    users.append(user)
                    self.stdout.write(f'Created user {i+1}/{user_count}: {user.username}')
                
                # Create food items
                self.stdout.write(self.style.SUCCESS(f'Creating {food_items_count} food items...'))
                foods = []
                public_foods = []
                
                for i in range(food_items_count):
                    is_public = random.random() < public_ratio
                    user = None if is_public else random.choice(users)
                    
                    food = FoodFactory(is_public=is_public, user=user)
                    foods.append(food)
                    
                    if is_public:
                        public_foods.append(food)
                
                # Generate historical data for each user
                self.stdout.write(self.style.SUCCESS(f'Generating {days_of_data} days of historical data...'))
                
                today = timezone.now().date()
                
                for day_offset in range(days_of_data):
                    target_date = today - timedelta(days=day_offset)
                    
                    for user in users:
                        # Not every user has data for every day (80% chance)
                        if random.random() < 0.8:
                            # Create 2-4 meals per day
                            meal_count = random.randint(2, 4)
                            for meal_num in range(meal_count):
                                # Distribute throughout the day
                                hour = 8 if meal_num == 0 else 12 if meal_num == 1 else 18 if meal_num == 2 else 15
                                minute = random.randint(0, 59)
                                
                                meal_time = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
                                meal_time = timezone.make_aware(meal_time)
                                
                                # Determine meal type based on time
                                if hour < 11:
                                    meal_type = 'breakfast'
                                elif hour < 15:
                                    meal_type = 'lunch'
                                elif hour < 17:
                                    meal_type = 'snack'
                                else:
                                    meal_type = 'dinner'
                                
                                meal = MealFactory(
                                    user=user,
                                    date_time=meal_time,
                                    meal_type=meal_type
                                )
                                
                                # Add 1-5 foods to each meal
                                food_count = random.randint(1, 5)
                                available_foods = public_foods + [f for f in foods if f.user == user]
                                
                                # Make sure we don't try to add more foods than available
                                food_count = min(food_count, len(available_foods))
                                
                                for _ in range(food_count):
                                    food = random.choice(available_foods)
                                    amount = random.randint(50, 500)  # grams
                                    MealFoodFactory(meal=meal, food=food, amount=amount)
                            
                            # Create health log (90% chance if user has meals that day)
                            if random.random() < 0.9:
                                HealthLogFactory(user=user, date=target_date)
                            
                            # Create sleep log (85% chance if user has meals that day)
                            if random.random() < 0.85:
                                SleepFactory(user=user, date=target_date)
                
                self.stdout.write(self.style.SUCCESS('Successfully populated database with fake data!'))
                self.stdout.write(self.style.SUCCESS(f'Created:'))
                self.stdout.write(f'- {user_count} users with profiles')
                self.stdout.write(f'- {food_items_count} food items')
                self.stdout.write(f'- Approximately {user_count * days_of_data * 0.8 * 3} meals')
                self.stdout.write(f'- Approximately {user_count * days_of_data * 0.8 * 0.9} health logs')
                self.stdout.write(f'- Approximately {user_count * days_of_data * 0.8 * 0.85} sleep logs')
                
                if create_admin:
                    self.stdout.write(self.style.SUCCESS('\nAdmin access:'))
                    self.stdout.write(f'URL: http://localhost:8000/admin/')
                    self.stdout.write(f'Username: admin@example.com')
                    self.stdout.write(f'Password: admin123')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error populating database: {str(e)}'))
            raise 
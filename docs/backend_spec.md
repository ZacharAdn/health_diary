# Backend Specification - Health Diary Backend

## Technologies
- Python 3.11+
- Django 5.0+
- Django REST Framework
- Simple JWT for authentication
- PostgreSQL
- Redis (for caching)
- Celery (for async tasks)

## Models

### User
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True)  # in cm
    is_medical_professional = models.BooleanField(default=False)
```

### Profile
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    goals = models.TextField(blank=True)
```

### Food
```python
class Food(models.Model):
    name = models.CharField(max_length=100)
    calories = models.IntegerField(null=True)
    protein = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    carbs = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    fats = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # for custom foods
    is_public = models.BooleanField(default=True)
```

### Meal
```python
class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    notes = models.TextField(blank=True)
```

### MealFood
```python
class MealFood(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2)  # in grams
    notes = models.TextField(blank=True)
```

### HealthLog
```python
class HealthLog(models.Model):
    STOOL_QUALITY = [
        ('hard', 'Hard and Dry'),
        ('normal', 'Normal'),
        ('soft', 'Soft'),
        ('diarrhea', 'Diarrhea'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    physical_feeling = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    mental_feeling = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    stool_count = models.IntegerField(default=0)
    stool_quality = models.CharField(max_length=20, choices=STOOL_QUALITY, null=True)
    complete_evacuation = models.BooleanField(null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)  # in kg
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
```

### Sleep
```python
class Sleep(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    duration = models.DecimalField(max_digits=4, decimal_places=2)  # in hours
    quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    wake_up_ease = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    energy_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    notes = models.TextField(blank=True)
```

## API Endpoints

### Authentication
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/token/refresh/
- POST /api/auth/logout/
- GET /api/auth/user/
- PUT /api/auth/user/

### Profile
- GET /api/profile/
- PUT /api/profile/
- PATCH /api/profile/

### Foods
- GET /api/foods/
- POST /api/foods/
- GET /api/foods/{id}/
- PUT /api/foods/{id}/
- DELETE /api/foods/{id}/
- GET /api/foods/search/

### Meals
- GET /api/meals/
- POST /api/meals/
- GET /api/meals/{id}/
- PUT /api/meals/{id}/
- DELETE /api/meals/{id}/
- GET /api/meals/daily/{date}/
- GET /api/meals/weekly/{date}/

### Health Logs
- GET /api/health-logs/
- POST /api/health-logs/
- GET /api/health-logs/{id}/
- PUT /api/health-logs/{id}/
- GET /api/health-logs/daily/{date}/
- GET /api/health-logs/weekly/{date}/
- GET /api/health-logs/monthly/{date}/

### Sleep
- GET /api/sleep/
- POST /api/sleep/
- GET /api/sleep/{id}/
- PUT /api/sleep/{id}/
- GET /api/sleep/weekly/{date}/
- GET /api/sleep/monthly/{date}/

### Analytics
- GET /api/analytics/health-trends/
- GET /api/analytics/food-correlations/
- GET /api/analytics/sleep-analysis/
- GET /api/analytics/symptoms-triggers/

## Security
- JWT Authentication
- CSRF protection
- Rate limiting
- Sensitive data encryption
- Role-based permissions
- Input validation on all endpoints

## Caching
- Redis for:
  - Food search results
  - Analytics and graphs
  - Logged-in user information

## Async Tasks (Celery)
- Sending notifications and reminders
- Data export
- Complex analytics processing
- Data backup

## Development Setup
- Docker containerization
- CI/CD with GitHub Actions
- Automated testing
- Swagger/OpenAPI documentation 
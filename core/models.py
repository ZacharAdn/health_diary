from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Extended user model with additional fields"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Height in centimeters"
    )
    is_medical_professional = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Profile(models.Model):
    """User profile with additional medical and personal information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    goals = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Food(models.Model):
    """Food items for meal tracking"""
    name = models.CharField(max_length=100)
    calories = models.IntegerField(null=True, blank=True)
    protein = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    carbs = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    fats = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='custom_foods'
    )
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Meal(models.Model):
    """Meal records for user food intake"""
    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast', _('Breakfast')
        LUNCH = 'lunch', _('Lunch')
        DINNER = 'dinner', _('Dinner')
        SNACK = 'snack', _('Snack')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    date_time = models.DateTimeField()
    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.user.username}'s {self.get_meal_type_display()} on {self.date_time.strftime('%Y-%m-%d %H:%M')}"

class MealFood(models.Model):
    """Foods included in a meal with amounts"""
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=7, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Amount in grams"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.amount}g of {self.food.name} in {self.meal}"

class HealthLog(models.Model):
    """Daily health log for tracking digestive health"""
    class StoolQuality(models.TextChoices):
        HARD = 'hard', _('Hard and Dry')
        NORMAL = 'normal', _('Normal')
        SOFT = 'soft', _('Soft')
        DIARRHEA = 'diarrhea', _('Diarrhea')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_logs')
    date = models.DateField()
    physical_feeling = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Physical feeling on a scale of 1-5"
    )
    mental_feeling = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Mental feeling on a scale of 1-5"
    )
    stool_count = models.IntegerField(default=0)
    stool_quality = models.CharField(
        max_length=20,
        choices=StoolQuality.choices,
        null=True,
        blank=True
    )
    complete_evacuation = models.BooleanField(null=True, blank=True)
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Weight in kilograms"
    )
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username}'s health log on {self.date}"

class Sleep(models.Model):
    """Sleep tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_logs')
    date = models.DateField()
    duration = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        help_text="Sleep duration in hours"
    )
    quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Sleep quality on a scale of 1-5"
    )
    wake_up_ease = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Ease of waking up on a scale of 1-5"
    )
    energy_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Energy level on a scale of 1-5"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username}'s sleep log on {self.date}"

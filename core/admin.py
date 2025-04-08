from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Food, Meal, MealFood, HealthLog, Sleep

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_medical_professional', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'date_of_birth', 'height', 'is_medical_professional')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'phone', 'date_of_birth', 'height', 'is_medical_professional')}),
    )
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_medical_professional', 'is_staff', 'is_active')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

class MealFoodInline(admin.TabularInline):
    model = MealFood
    extra = 1
    raw_id_fields = ('food',)

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'protein', 'carbs', 'fats', 'is_public', 'user')
    list_filter = ('is_public',)
    search_fields = ('name',)
    raw_id_fields = ('user',)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'date_time', 'meal_type')
    list_filter = ('meal_type', 'date_time')
    search_fields = ('user__username', 'user__email', 'notes')
    raw_id_fields = ('user',)
    inlines = [MealFoodInline]
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'physical_feeling', 'mental_feeling', 'stool_count', 'stool_quality')
    list_filter = ('date', 'physical_feeling', 'mental_feeling', 'stool_quality')
    search_fields = ('user__username', 'user__email', 'symptoms', 'notes')
    raw_id_fields = ('user',)

@admin.register(Sleep)
class SleepAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'duration', 'quality', 'energy_level')
    list_filter = ('date', 'quality', 'energy_level')
    search_fields = ('user__username', 'user__email', 'notes')
    raw_id_fields = ('user',)

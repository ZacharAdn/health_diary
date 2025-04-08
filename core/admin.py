# Temporarily disable all admin configuration 
# from django.contrib import admin
# # Temporarily comment out the UserAdmin import until we resolve the issue
# # from django.contrib.auth.admin import UserAdmin
# from .models import User, Profile, Food, Meal, MealFood, HealthLog, Sleep
# from .admin_site import health_diary_admin
# 
# # Register models with custom admin site instead of default admin site
# @health_diary_admin.register(User)
# class CustomUserAdmin(admin.ModelAdmin):  # Change to ModelAdmin instead of UserAdmin
#     list_display = ('username', 'email', 'is_medical_professional', 'is_staff')
#     # Comment out the UserAdmin specific fields
#     # fieldsets = UserAdmin.fieldsets + (
#     #     ('Additional Info', {'fields': ('phone', 'date_of_birth', 'height', 'is_medical_professional')}),
#     # )
#     # add_fieldsets = UserAdmin.add_fieldsets + (
#     #     ('Additional Info', {'fields': ('email', 'phone', 'date_of_birth', 'height', 'is_medical_professional')}),
#     # )
#     # Add a simple fieldsets configuration
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'height')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_medical_professional', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     search_fields = ('username', 'email', 'phone')
#     list_filter = ('is_medical_professional', 'is_staff', 'is_active')
# 
# @health_diary_admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'get_email')
#     search_fields = ('user__username', 'user__email')
#     raw_id_fields = ('user',)
#     
#     def get_email(self, obj):
#         return obj.user.email
#     get_email.short_description = 'Email'
#     get_email.admin_order_field = 'user__email'
# 
# class MealFoodInline(admin.TabularInline):
#     model = MealFood
#     extra = 1
#     raw_id_fields = ('food',)
# 
# @health_diary_admin.register(Food)
# class FoodAdmin(admin.ModelAdmin):
#     list_display = ('name', 'calories', 'protein', 'carbs', 'fats', 'is_public', 'user')
#     list_filter = ('is_public',)
#     search_fields = ('name',)
#     raw_id_fields = ('user',)
# 
# @health_diary_admin.register(Meal)
# class MealAdmin(admin.ModelAdmin):
#     list_display = ('user', 'get_email', 'date_time', 'meal_type')
#     list_filter = ('meal_type', 'date_time')
#     search_fields = ('user__username', 'user__email', 'notes')
#     raw_id_fields = ('user',)
#     inlines = [MealFoodInline]
#     
#     def get_email(self, obj):
#         return obj.user.email
#     get_email.short_description = 'Email'
#     get_email.admin_order_field = 'user__email'
# 
# @health_diary_admin.register(HealthLog)
# class HealthLogAdmin(admin.ModelAdmin):
#     list_display = ('user', 'date', 'physical_feeling', 'mental_feeling', 'stool_count', 'stool_quality')
#     list_filter = ('date', 'physical_feeling', 'mental_feeling', 'stool_quality')
#     search_fields = ('user__username', 'user__email', 'symptoms', 'notes')
#     raw_id_fields = ('user',)
# 
# @health_diary_admin.register(Sleep)
# class SleepAdmin(admin.ModelAdmin):
#     list_display = ('user', 'date', 'duration', 'quality', 'energy_level')
#     list_filter = ('date', 'quality', 'energy_level')
#     search_fields = ('user__username', 'user__email', 'notes')
#     raw_id_fields = ('user',)

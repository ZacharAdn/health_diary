from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView,
    ProfileView,
    FoodViewSet,
    MealViewSet,
    HealthLogViewSet,
    SleepViewSet,
    AnalyticsViewSet,
    UserView,
    ExportViewSet,
)

router = DefaultRouter()
router.register(r'foods', FoodViewSet, basename='food')
router.register(r'meals', MealViewSet, basename='meal')
router.register(r'health-logs', HealthLogViewSet, basename='healthlog')
router.register(r'sleep', SleepViewSet, basename='sleep')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'export', ExportViewSet, basename='export')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User management
    path('user/', UserView.as_view(), name='user-detail'),
    path('user/delete/', UserView.as_view(), name='user-delete'),
    
    # Profile endpoint
    path('profile/', ProfileView.as_view(), name='profile-detail'),
    
    # Router URLs
    path('', include(router.urls)),
    
    # Custom date-based endpoints
    path('meals/daily/<str:date>/', MealViewSet.as_view({'get': 'daily'}), name='meal-daily'),
    path('meals/weekly/<str:date>/', MealViewSet.as_view({'get': 'weekly'}), name='meal-weekly'),
    
    path('health-logs/daily/<str:date>/', HealthLogViewSet.as_view({'get': 'daily'}), name='healthlog-daily'),
    path('health-logs/weekly/<str:date>/', HealthLogViewSet.as_view({'get': 'weekly'}), name='healthlog-weekly'),
    path('health-logs/monthly/<str:date>/', HealthLogViewSet.as_view({'get': 'monthly'}), name='healthlog-monthly'),
    
    path('sleep/weekly/<str:date>/', SleepViewSet.as_view({'get': 'weekly'}), name='sleep-weekly'),
    path('sleep/monthly/<str:date>/', SleepViewSet.as_view({'get': 'monthly'}), name='sleep-monthly'),
    
    # Export endpoints
    path('export/health-data/', ExportViewSet.as_view({'get': 'health_data'}), name='export-health-data'),
    path('export/meal-data/', ExportViewSet.as_view({'get': 'meal_data'}), name='export-meal-data'),
    path('export/all-data/', ExportViewSet.as_view({'get': 'all_data'}), name='export-all-data'),
] 
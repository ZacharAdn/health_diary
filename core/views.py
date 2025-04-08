from django.shortcuts import render
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Profile, Food, Meal, MealFood, HealthLog, Sleep
from .serializers import (
    UserSerializer, 
    ProfileSerializer, 
    FoodSerializer, 
    MealSerializer, 
    HealthLogSerializer, 
    SleepSerializer,
    RegisterSerializer,
)
from .services import HealthAnalyticsService

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        # Add token to response
        response_data = serializer.data
        response_data['token'] = str(refresh.access_token)
        
        return Response(response_data, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for user profile"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return Profile.objects.get(user=self.request.user)

@extend_schema_view(
    list=extend_schema(
        description="List all foods accessible to the user (public or owned)",
        parameters=[
            OpenApiParameter(name="search", description="Search foods by name", required=False, type=str),
        ]
    ),
    search=extend_schema(
        description="Search foods by name or nutritional content",
        parameters=[
            OpenApiParameter(name="query", description="Search query", required=True, type=str),
        ]
    )
)
class FoodViewSet(viewsets.ModelViewSet):
    """API endpoint for food items"""
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        """Return foods that are public or owned by the user"""
        return Food.objects.filter(
            Q(is_public=True) | Q(user=self.request.user)
        )
        
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for food items"""
        query = request.query_params.get('query', '')
        if not query:
            return Response(
                {"error": "Query parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        foods = self.get_queryset().filter(name__icontains=query)
        serializer = self.get_serializer(foods, many=True)
        return Response(serializer.data)

@extend_schema_view(
    daily=extend_schema(
        description="Get meals for a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Date in YYYY-MM-DD format", required=True, type=str),
        ]
    ),
    weekly=extend_schema(
        description="Get meals for a week starting at a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Starting date in YYYY-MM-DD format", required=True, type=str),
        ]
    )
)
class MealViewSet(viewsets.ModelViewSet):
    """API endpoint for meals"""
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return meals for the current user"""
        return Meal.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def daily(self, request, date=None):
        """Get meals for a specific day"""
        try:
            if date:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                target_date = timezone.now().date()
                
            meals = self.get_queryset().filter(
                date_time__date=target_date
            ).order_by('date_time')
            
            serializer = self.get_serializer(meals, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def weekly(self, request, date=None):
        """Get meals for a week starting at a specific date"""
        try:
            if date:
                start_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                start_date = timezone.now().date()
                
            end_date = start_date + timedelta(days=6)
            
            # Debug logging to understand the date range
            print(f"Weekly meals query: start_date={start_date}, end_date={end_date}")
            
            # Get all meals within date range
            meals = self.get_queryset().filter(
                date_time__date__gte=start_date,
                date_time__date__lte=end_date
            ).order_by('date_time')
            
            # Debug counts
            print(f"Found {meals.count()} meals in date range")
            
            # Print meals details for debugging
            for meal in meals:
                print(f"Meal: {meal.id}, date: {meal.date_time.date()}, type: {meal.meal_type}")
            
            # List ALL meals
            all_meals = self.get_queryset()
            print(f"Total meals in database: {all_meals.count()}")
            if all_meals.count() > 0:
                for meal in all_meals:
                    print(f"ALL Meal: {meal.id}, date: {meal.date_time.date()}, type: {meal.meal_type}")
            
            serializer = self.get_serializer(meals, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema_view(
    daily=extend_schema(
        description="Get health log for a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Date in YYYY-MM-DD format", required=True, type=str),
        ]
    ),
    weekly=extend_schema(
        description="Get health logs for a week starting at a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Starting date in YYYY-MM-DD format", required=True, type=str),
        ]
    ),
    monthly=extend_schema(
        description="Get health logs for a month starting at a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Starting date in YYYY-MM-DD format", required=True, type=str),
        ]
    )
)
class HealthLogViewSet(viewsets.ModelViewSet):
    """API endpoint for health logs"""
    serializer_class = HealthLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return health logs for the current user"""
        return HealthLog.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def daily(self, request, date=None):
        """Get health log for a specific day"""
        try:
            if date:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                target_date = timezone.now().date()
                
            try:
                health_log = self.get_queryset().get(date=target_date)
                serializer = self.get_serializer(health_log)
                return Response(serializer.data)
            except HealthLog.DoesNotExist:
                return Response(
                    {"detail": "No health log found for this date"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def weekly(self, request, date=None):
        """Get health logs for a week starting at a specific date"""
        try:
            if date:
                start_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                start_date = timezone.now().date()
                
            end_date = start_date + timedelta(days=6)
            
            health_logs = self.get_queryset().filter(
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            serializer = self.get_serializer(health_logs, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def monthly(self, request, date=None):
        """Get health logs for a month starting at a specific date"""
        try:
            if date:
                start_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                start_date = timezone.now().date().replace(day=1)
                
            # Calculate end of month
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
            
            health_logs = self.get_queryset().filter(
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            serializer = self.get_serializer(health_logs, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema_view(
    weekly=extend_schema(
        description="Get sleep logs for a week starting at a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Starting date in YYYY-MM-DD format", required=True, type=str),
        ]
    ),
    monthly=extend_schema(
        description="Get sleep logs for a month starting at a specific date",
        parameters=[
            OpenApiParameter(name="date", description="Starting date in YYYY-MM-DD format", required=True, type=str),
        ]
    )
)
class SleepViewSet(viewsets.ModelViewSet):
    """API endpoint for sleep logs"""
    serializer_class = SleepSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return sleep logs for the current user"""
        return Sleep.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def weekly(self, request, date=None):
        """Get sleep logs for a week starting at a specific date"""
        try:
            if date:
                start_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                start_date = timezone.now().date()
                
            end_date = start_date + timedelta(days=6)
            
            sleep_logs = self.get_queryset().filter(
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            serializer = self.get_serializer(sleep_logs, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def monthly(self, request, date=None):
        """Get sleep logs for a month starting at a specific date"""
        try:
            if date:
                start_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                start_date = timezone.now().date().replace(day=1)
                
            # Calculate end of month
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
            
            sleep_logs = self.get_queryset().filter(
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            serializer = self.get_serializer(sleep_logs, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class AnalyticsViewSet(viewsets.ViewSet):
    """API endpoints for analytics and insights"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def health_trends(self, request):
        """Get health trends over time"""
        days = int(request.query_params.get('days', 30))
        user = request.user
        
        # Debug logging
        print(f"Fetching health trends for user {user.id} for the last {days} days")
        
        # Get the date range
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        print(f"Date range: {start_date} to {end_date}")
        
        # Check if there are any health logs
        health_logs_count = HealthLog.objects.filter(user=user).count()
        print(f"Total health logs for user: {health_logs_count}")
        
        # Check for health logs in the date range
        health_logs_in_range = HealthLog.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).count()
        print(f"Health logs in date range: {health_logs_in_range}")
        
        # Get trends
        trends = HealthAnalyticsService.get_health_trends(user, days)
        print(f"Trends: {trends}")
        
        return Response(trends)
    
    @action(detail=False, methods=['get'])
    def food_correlations(self, request):
        """Analyze correlation between foods and health metrics"""
        days = int(request.query_params.get('days', 30))
        correlations = HealthAnalyticsService.get_food_correlations(request.user, days)
        return Response(correlations)
    
    @action(detail=False, methods=['get'])
    def sleep_analysis(self, request):
        """Analyze sleep patterns"""
        days = int(request.query_params.get('days', 30))
        analysis = HealthAnalyticsService.analyze_sleep(request.user, days)
        return Response(analysis)
    
    @action(detail=False, methods=['get'])
    def symptoms_triggers(self, request):
        """Identify potential food triggers for symptoms"""
        days = int(request.query_params.get('days', 60))
        triggers = HealthAnalyticsService.identify_symptom_triggers(request.user, days)
        return Response(triggers)
        
    @action(detail=False, methods=['get'])
    def detailed_analysis(self, request):
        """Detailed health analysis (only for medical professionals)"""
        user = request.user
        if not user.is_medical_professional:
            return Response(
                {"detail": "You don't have permission to access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Advanced analytics for medical professionals would go here
        return Response({"detail": "Detailed analysis available"})

class UserView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for user account management"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExportViewSet(viewsets.ViewSet):
    """API endpoints for data export"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def health_data(self, request):
        """Export health log data to JSON"""
        health_logs = HealthLog.objects.filter(user=request.user)
        serializer = HealthLogSerializer(health_logs, many=True)
        return Response({
            'health_logs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def meal_data(self, request):
        """Export meal data to JSON"""
        meals = Meal.objects.filter(user=request.user)
        serializer = MealSerializer(meals, many=True)
        return Response({
            'meals': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def all_data(self, request):
        """Export all user data to JSON"""
        user = request.user
        
        # Get profile or create one if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            print(f"Created new profile for user {user.id}")
            
        meals = Meal.objects.filter(user=user)
        health_logs = HealthLog.objects.filter(user=user)
        sleep_logs = Sleep.objects.filter(user=user)
        
        user_serializer = UserSerializer(user)
        profile_serializer = ProfileSerializer(profile)
        meal_serializer = MealSerializer(meals, many=True)
        health_log_serializer = HealthLogSerializer(health_logs, many=True)
        sleep_serializer = SleepSerializer(sleep_logs, many=True)
        
        return Response({
            'user': user_serializer.data,
            'profile': profile_serializer.data,
            'meals': meal_serializer.data,
            'health_logs': health_log_serializer.data,
            'sleep_logs': sleep_serializer.data
        })

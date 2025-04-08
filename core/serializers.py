from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Food, Meal, MealFood, HealthLog, Sleep

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'phone', 
                  'date_of_birth', 'height', 'is_medical_professional', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if 'password' in attrs and 'password2' in attrs:
            if attrs['password'] != attrs.pop('password2'):
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        if 'password' not in validated_data:
            raise serializers.ValidationError({"password": "Password is required for user creation."})
            
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            **{key: validated_data[key] for key in validated_data if key not in ['username', 'email', 'password']}
        )
        
        # Create a default empty profile for the user
        Profile.objects.create(user=user)
        
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'medical_conditions', 'allergies', 'dietary_restrictions', 'goals')
        read_only_fields = ('id',)
        
    def create(self, validated_data):
        # If user isn't specified explicitly and we have a request context
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id', 'name', 'calories', 'protein', 'carbs', 'fats', 'user', 'is_public')
        read_only_fields = ('id',)
        
    def create(self, validated_data):
        # If user isn't specified explicitly and we have a request context
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class MealFoodSerializer(serializers.ModelSerializer):
    food_id = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all(),
        source='food',
        write_only=True
    )
    food_name = serializers.ReadOnlyField(source='food.name')
    
    class Meta:
        model = MealFood
        fields = ('id', 'food_id', 'food_name', 'amount', 'notes')
        read_only_fields = ('id',)

class MealSerializer(serializers.ModelSerializer):
    mealfood_set = MealFoodSerializer(many=True, read_only=True)
    foods = MealFoodSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Meal
        fields = ('id', 'user', 'date_time', 'meal_type', 'notes', 'mealfood_set', 'foods')
        read_only_fields = ('id',)
        
    def create(self, validated_data):
        foods_data = validated_data.pop('foods', [])
        
        # If user isn't specified explicitly and we have a request context
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user
            
        meal = Meal.objects.create(**validated_data)
        
        for food_data in foods_data:
            MealFood.objects.create(meal=meal, **food_data)
            
        return meal
        
    def update(self, instance, validated_data):
        foods_data = validated_data.pop('foods', None)
        
        # Update the meal's fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If foods were provided, update them
        if foods_data is not None:
            # Remove existing foods
            instance.mealfood_set.all().delete()
            
            # Add new foods
            for food_data in foods_data:
                MealFood.objects.create(meal=instance, **food_data)
                
        return instance

class HealthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthLog
        fields = ('id', 'user', 'date', 'physical_feeling', 'mental_feeling', 
                  'stool_count', 'stool_quality', 'complete_evacuation', 
                  'weight', 'symptoms', 'notes')
        read_only_fields = ('id',)
        
    def create(self, validated_data):
        # If user isn't specified explicitly and we have a request context
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user
            
        # Check for existing health log for this user and date
        user = validated_data.get('user')
        date = validated_data.get('date')
        
        if HealthLog.objects.filter(user=user, date=date).exists():
            raise serializers.ValidationError(
                {"date": "A health log for this date already exists."}
            )
            
        return super().create(validated_data)

class SleepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sleep
        fields = ('id', 'user', 'date', 'duration', 'quality', 
                  'wake_up_ease', 'energy_level', 'notes')
        read_only_fields = ('id',)
        
    def create(self, validated_data):
        # If user isn't specified explicitly and we have a request context
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user
            
        # Check for existing sleep log for this user and date
        user = validated_data.get('user')
        date = validated_data.get('date')
        
        if Sleep.objects.filter(user=user, date=date).exists():
            raise serializers.ValidationError(
                {"date": "A sleep log for this date already exists."}
            )
            
        return super().create(validated_data)

# Serializer for user registration with token response
class RegisterSerializer(UserSerializer):
    token = serializers.CharField(read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('token',) 
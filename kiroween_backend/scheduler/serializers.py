"""
Serializers for the Phantom scheduler application.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Event, Category


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with username, name, and password validation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,  # Don't strip whitespace from passwords
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,  # Don't strip whitespace from passwords
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'name', 'password', 'password_confirm']
        extra_kwargs = {
            'username': {'required': True},
            'name': {'required': True},
        }

    def validate_username(self, value):
        """
        Check that the username is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        """
        Validate password using Django's password validators.
        """
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """
        Check that the two password fields match.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user with hashed password.
        """
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event model with all fields and validation.
    Includes custom validation for date/time constraints.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_priority = serializers.IntegerField(source='category.priority_level', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'user', 'title', 'description', 'category', 'category_name', 
            'category_priority', 'start_time', 'end_time', 'is_flexible', 
            'is_completed', 'google_calendar_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'google_calendar_id']
    
    def validate(self, attrs):
        """
        Validate that end_time is after start_time.
        """
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        # For updates, get existing values if not provided
        if self.instance:
            start_time = start_time or self.instance.start_time
            end_time = end_time or self.instance.end_time
        
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        return attrs
    
    def validate_category(self, value):
        """
        Validate that the category exists.
        """
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError('Invalid category.')
        return value


class EventListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for event list views.
    Includes only essential fields for better performance.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_priority = serializers.IntegerField(source='category.priority_level', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'category_name', 'category_priority',
            'start_time', 'end_time', 'is_flexible', 'is_completed'
        ]
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'priority_level', 'color', 'description']
        read_only_fields = ['id']


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences (timezone, default_event_duration).
    """
    class Meta:
        model = User
        fields = ['timezone', 'default_event_duration']

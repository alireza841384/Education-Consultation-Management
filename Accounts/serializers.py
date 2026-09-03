from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import CustomUser , UserProfile
from django.db import transaction
from django.contrib.auth.password_validation import validate_password

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['birth_year', 'national_id', 'photo']
        extra_kwargs = {
            'national_id': {'read_only' : True}
        }

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'profile', 'date_joined','type']
        read_only_fields = ['id', 'email', 'date_joined']

    
    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance  
    
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise ValidationError({"password": "Passwords do not match."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = CustomUser.objects.create_user(**validated_data)
        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    """Serializer for the first step: receive the user's email."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for the second step: verify token and set the new password."""
    email = serializers.EmailField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        # Apply AUTH_PASSWORD_VALIDATORS rules from settings
        validate_password(value)
        return value
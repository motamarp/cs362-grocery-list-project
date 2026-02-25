from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

# Create your serializers here.
class UserProfileSerializer(serializers.ModelSerializer):
    # Serializer for UserProfile
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 
            'username', 
            'first_name',
            'last_name',
            'full_name',
            'date_of_birth',
            'height',
            'dietary_preferences',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    #Serializer for User model with profile data
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
            'profile',
            'date_joined'
        ]
        read_only_fields = ['date_joined']
    
    def validate(self, data):
        #Validate that passwords match
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data
    
    def create(self, validated_data):
        #Create a new user with hashed password
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    #Serializer for updating basic info
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    #Serializer for updating profile info
    
    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth',
            'height',
            'dietary_preferences',
            'favorite_stores'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    #Serializer for password change
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, data):
        #Again validate that passwords match
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "New passwords must match."})
        return data
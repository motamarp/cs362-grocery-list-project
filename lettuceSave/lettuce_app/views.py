from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.

from .models import UserProfile
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    UserUpdateSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer
)

class UserRegistrationView(APIView):
    """ View for user registration """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ ViewSet for user profiles
    Endpoints:
    - GET /api/profiles/ - List all profiles (admin)
    - GET /api/profiles/me/ - Get current user's profile
    - GET /api/profiles/{id}/ - Get specific profile
    - PUT/PATCH /api/profiles/me/ - Update current user's profile
    - POST /api/profiles/me/change-password/ - Change password
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """ Get or update current user's profile """
        profile = request.user.profile
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            # Update user basic info if provided
            user_data = {}
            if 'first_name' in request.data:
                user_data['first_name'] = request.data.pop('first_name')
            if 'last_name' in request.data:
                user_data['last_name'] = request.data.pop('last_name')
            
            if user_data:
                user_serializer = UserUpdateSerializer(
                    request.user, 
                    data=user_data, 
                    partial=True
                )
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return Response(
                        user_serializer.errors, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update profile
            profile_serializer = ProfileUpdateSerializer(
                profile, 
                data=request.data, 
                partial=True
            )
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response(UserProfileSerializer(profile).data)
            return Response(
                profile_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """ Change user password """
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Wrong password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {'message': 'Password updated successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
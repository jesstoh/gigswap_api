from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from accounts.models import User, TalentProfile, HirerProfile
from accounts.serializers import UserSerializer, HirerProfileSerializer, TalentProfileSerializer
from talents.models import TalentFav
from hirers.models import HirerFav

# Create your views here.


@api_view(['POST'])
# @authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    if request.method == 'POST':
        user = UserSerializer(data=request.data)
        if user.is_valid(raise_exception=True):
            user.save()
            user_obj = User.objects.get(pk=user.data['id'])
            # Create a fav object if user is talent
            if not user_obj.is_hirer:
                TalentFav.objects.create(user=user_obj)
            elif (user_obj.is_hirer) and (not user_obj.is_staff):
                # Create a HirerFav object if user is hirer and not admin
                HirerFav.objects.create(user=user_obj)

            # Login after register
            # return Response(user.data)
            # to change to login later
            refresh = RefreshToken.for_user(user_obj)
            user_serialized = UserSerializer(user_obj)
            return Response(
                {'refresh': str(refresh),
                 'access': str(refresh.access_token),
                 'user': user_serialized.data,
                 'message': 'user registered'}
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']

        if (username is None) or (password is None):
            raise exceptions.AuthenticationFailed(
                {'details': 'username or password is required'})

        user = User.objects.filter(username=username).first()
        if user is None:
            raise exceptions.AuthenticationFailed(
                {'details': 'user not found'})
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(
                {'details': 'wrong password'})

        user_serialized = UserSerializer(user).data

        refresh = RefreshToken.for_user(user)

        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'user': user_serialized})

# Create, edit and get profile of login hirer or talent


@api_view(['GET', 'PUT', 'POST'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if user.is_profile_complete:
            raise exceptions.PermissionDenied(
                {'detail': 'Profile only exists'})
        else:
            if user.is_hirer:
                profile = HirerProfileSerializer(
                    data=request.data, context={'request': request})
            else:
                profile = TalentProfileSerializer(
                    data=request.data, context={'request': request})
            if profile.is_valid(raise_exception=True):
                profile.save()
                user.is_profile_complete = True
                user.save()
                return Response(profile.data)

    # Check if profile exists for get and put route
    if not user.is_profile_complete:
        raise exceptions.NotFound({'detail': 'Profile not found'})

    # Get profile of user
    if request.method == 'GET':
        # Find profile of user
        if user.is_hirer:
            profile = HirerProfile.objects.get(user=user)
            profile_serialized = HirerProfileSerializer(profile)
        else:
            profile = TalentProfile.objects.get(user=user)
            profile_serialized = TalentProfileSerializer(profile)
        return Response(profile_serialized.data)
   # Edit profile
    else:
        if user.is_hirer:
            profile = HirerProfile.objects.get(user=user)
            profile = HirerProfileSerializer(
                instance=profile, data=request.data)
        else:
            profile = TalentProfile.objects.get(user=user)
            profile = TalentProfileSerializer(
                instance=profile, data=request.data, context={'request': request})
        if profile.is_valid(raise_exception=True):
            profile.save()
            return Response(profile.data)


# Check authentication based on access token
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_view(request):
    user = request.user
    data = {
        'isAuthenticated': True,
        'isHirer': False,
        'isAdmin': False,
        'user': {'username': user.username}
    }
    if user.is_hirer: 
        data['isHirer'] = True
    elif user.is_staff:
        data['isAdmin'] = True

    return Response(data)
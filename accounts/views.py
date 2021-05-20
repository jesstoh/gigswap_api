from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from accounts.models import User
from accounts.serializers import UserSerializer
from talents.models import TalentFav

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
            #Create a fav object if user is talent
            if not user_obj.is_hirer:
                TalentFav.objects.create(user=user_obj)
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

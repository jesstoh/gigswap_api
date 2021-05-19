from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.decorators import api_view
from rest_framework import exceptions
from django.core.exceptions import ValidationError
from accounts.models import User
from accounts.serializers import UserSerializer

# Create your views here.
@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        user = UserSerializer(data=request.data)
        if user.is_valid(raise_exception=True):
            user.save()
            #to change to login later
            return Response({'message': 'User registered'})

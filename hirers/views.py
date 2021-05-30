from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import exceptions
from rest_framework import status
from accounts.models import User
from hirers.models import HirerFav
from hirers.serializers import HirerFavSerializer, HirerDetailSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_index(request):
    if not request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail':'Only hirer can view saved or hired talents'})
    hirer_fav = HirerFav.objects.get(user=request.user)
    hirer_fav_serialized = HirerFavSerializer(hirer_fav)
    return Response(hirer_fav_serialized.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_show(request, id):
    #Check if hirer exists
    try:
        hirer = User.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Hirer not found'})
    # Check if hirer completed the profile
    if not hirer.is_profile_complete:
        raise exceptions.NotFound({'detail':'Hirer profile not found'})

    hirer_details = HirerDetailSerializer(hirer)
    return Response(hirer_details.data)
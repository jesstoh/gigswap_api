from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import exceptions
from rest_framework import status
from hirers.models import HirerFav
from hirers.serializers import HirerFavSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def index_view(request):
    if not request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail':'Only hirer can view saved or hired talents'})
    hirer_fav = HirerFav.objects.get(user=request.user)
    hirer_fav_serialized = HirerFavSerializer(hirer_fav)
    return Response(hirer_fav_serialized.data)
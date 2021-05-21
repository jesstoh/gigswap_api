from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from accounts.models import User, TalentProfile
from accounts.serializers import TalentProfileSerializer

# Create your views here.

#Get all talents profiles
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_index(request):
    user = request.user
    #Only hirers or admin can access list of talents
    if user.is_hirer or user.is_staff:
        talents = TalentProfile.objects.all()
        talents_serialized = TalentProfileSerializer(talents, many=True)
        return Response(talents_serialized.data)
    else:
        raise exceptions.PermissionDenied({'detail': 'Only hirers or admin can access talents list'})
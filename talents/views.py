from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from accounts.models import User, TalentProfile
from accounts.serializers import TalentProfileSerializer
from talents.serializers import TalentDetailSerializer, TalentFavSerializer
from talents.models import TalentFav

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


#Show detail of talent
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_show(request, id):
    #Check if talent exists
    try:
        talent = User.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Talent not found'})
    # Check if talent completed the profile
    if not talent.is_profile_complete:
        raise exceptions.NotFound({'detail':'Talent profile not found'})

    talent_details = TalentDetailSerializer(talent)
    return Response(talent_details.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_fav(request):
    try:
        talent_fav = TalentFav.objects.get(user=request.user)
    except:
        raise exceptions.NotFound({'detail': 'Talent favorite list not found'})

    talent_fav_serialized = TalentFavSerializer(talent_fav)
    return Response(talent_fav_serialized.data)

    
from django.shortcuts import render
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response 
from rest_framework import exceptions
from rest_framework import status
from django.utils import timezone
from accounts.models import User
from accounts.serializers import UserSerializer
from gigs.models import Gig
from gigs.serializers import GigBriefSerializer

# Create your views here.

#Get summary of gigs app
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_view(request):
    hirers_count = User.objects.filter(is_hirer=True).count()
    talents_count = User.objects.filter(is_hirer=False, is_staff=False).count()
    gigs_count = Gig.objects.all().count()
    active_gigs_count = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date()).count()
    return Response({'hirersCount': hirers_count, 'talentsCount': talents_count, 'gigsCount': gigs_count, 'activeGigsCount': active_gigs_count })

#Get all users list
@api_view(['GET'])
@permission_classes([IsAdminUser])
def users_view(request):
    talents = User.objects.filter(is_hirer=False, is_staff=False).order_by('-date_joined')
    hirers = User.objects.filter(is_hirer=True).order_by('-date_joined')
    talents_serialized = UserSerializer(talents, many=True)
    hirers_serialized = UserSerializer(hirers, many=True)
    return Response({'talents': talents_serialized.data, 'hirers': hirers_serialized.data})

#Deactivate user
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def deactivate_view(request, userId):
    try:
        user = User.objects.get(pk=userId)
    except:
        raise exceptions.NotFound({'detail': 'User not found'})

    #Check if user is active
    if not user.is_active:
        return Response({'detail': 'Cannot deactivate inactive user'}, status=status.HTTP_412_PRECONDITION_FAILED)

    #Deactivate user
    user.is_active = False
    user.save()
    return Response({'message': 'User deactivated'})

#Activate user
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def activate_view(request, userId):
    try:
        user = User.objects.get(pk=userId)
    except:
        raise exceptions.NotFound({'detail': 'User not found'})

    #Check if user is inactive
    if user.is_active:
        return Response({'detail': 'Cannot activate active user'}, status=status.HTTP_412_PRECONDITION_FAILED)

    #Activate user
    user.is_active = True
    user.save()
    return Response({'message': 'User activated'})

#Get all active and inactive gigs
@api_view(['GET'])
@permission_classes([IsAdminUser])
def gigs_index_view(request):

    if request.GET.get('active') == 'True':
        # Filter not expired gigs & order by number of flags
        gigs = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date()).annotate(flag_count = Count('flag')).order_by('-flag_count')   
    else:
        gigs = Gig.objects.all().order_by('-created_at')

    gigs_serialized = GigBriefSerializer(gigs, many=True)

    return Response(gigs_serialized.data)
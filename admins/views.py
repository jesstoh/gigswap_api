from django.shortcuts import render
from django.db.models import Count, Q
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
from categories.models import Category, Subcategory

# Create your views here.

#Get summary of gigs app
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_view(request):

    #User related stats
    users_count = User.objects.filter(is_staff=False).count()
    profile_complete_rate = round(User.objects.filter(is_profile_complete=True).count() / users_count *100)
    hirers_count = User.objects.filter(is_hirer=True).count()
    talents_count = User.objects.filter(is_hirer=False, is_staff=False).count()

    #Gigs related stats
    gigs_count = Gig.objects.all().count()
    active_gigs_count = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gte=timezone.now().date()).count()

    gigs_expired_count = Gig.objects.filter(is_closed=False)
    gigs_expired_count = gigs_expired_count.filter(Q(expired_at__lt=timezone.now().date()) | Q(winner__isnull=False)).distinct().count()
    gigs_award_count = Gig.objects.filter(winner__isnull=False).count()
    if gigs_expired_count and gigs_award_count:
        gigs_award_rate = round(gigs_award_count / gigs_expired_count * 100)

    gigs_cancel_count = Gig.objects.filter(is_closed=True).count()
    if gigs_count and gigs_cancel_count:
        gigs_cancel_rate = round(gigs_cancel_count / gigs_count * 100)
    else:
        gigs_cancel_rate = 0

    
    #Category related stats
    category_count = Category.objects.all().count()
    subcategory_count = Subcategory.objects.all().count()

    return Response({'usersCount': users_count, 'hirersCount': hirers_count, 'talentsCount': talents_count, 'profileCompleteRate': profile_complete_rate,'gigsCount': gigs_count, 'activeGigsCount': active_gigs_count, 'gigsCancelRate': gigs_cancel_rate, 'gigsAwardRate': gigs_award_rate, 'categoryCount': category_count, 'subcatCount': subcategory_count })

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

    if request.GET.get('active') == 'true':
        # Filter not expired gigs & order by number of flags
        gigs = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date()).annotate(flag_count = Count('flag')).order_by('-flag_count')   
    else:
        gigs = Gig.objects.all().order_by('-created_at')

    gigs_serialized = GigBriefSerializer(gigs, many=True)

    return Response(gigs_serialized.data)
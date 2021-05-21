import os
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import exceptions
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from gigs.models import Gig
from categories.models import Subcategory
from gigs.serializers import GigSerializer
from accounts.models import User
from talents.models import TalentFav
from notifications.models import Notification

# Get base url of front end 
BASE_URL = os.environ['BASE_URL']

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def index_view(request):
    if request.method == 'POST':
        if not request.user.is_hirer:
            raise exceptions.PermissionDenied({'detail': 'Only hirer can create gig listing'})
        gig = GigSerializer(data=request.data, context={'request':request})
        if gig.is_valid(raise_exception=True):
            gig.save()
        return Response(gig.data, status=status.HTTP_201_CREATED)
    if request.method == 'GET':
        gigs = Gig.objects.all()
        gigs_serializer = GigSerializer(gigs, many=True)
        return Response(gigs_serializer.data)

def recommend_gig_view(request):
    pass

@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def show_view(request, id):
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    
    user = request.user
    if request.method == 'GET':
        gig_serialized = GigSerializer(gig)
        return Response (gig_serialized.data)
    elif request.method == 'PUT':
        #Only gig owner can update gig
        if user != gig.poster:
            raise exceptions.PermissionDenied({'detail': 'Only gig poster can update gig'})
        gig = GigSerializer(data=request.data, instance=gig, context={'request':request})
        if gig.is_valid(raise_exception=True):
            gig.save()
        return Response(gig.data)
    elif request.method == 'DELETE':
        #Only admin or gig owner can delete gig
        if (user != gig.poster) and (not user.is_staff):
            raise exceptions.PermissionDenied({'detail': 'Only gig poster or admin can delete gig'})
        gig.delete()
        return Response({'message': 'delete success'})
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def save_view(request, id):
    #Check if gig exists
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    #Check if user is talent, only talent can save gig
    if request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail': 'Only talent can save gig'})
    talent_fav = TalentFav.objects.get(user=request.user)
    talent_fav.saved.add(gig)
    return Response({'message': 'Gig saved'})

@api_view(['PUT'])    
@permission_classes([IsAuthenticated])
def unsave_view(request, id):
    #Check if gig exists
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    #Check if user is talent, only talent can unsave gig
    if request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail': 'Only talent can unsave gig'})
    talent_fav = TalentFav.objects.get(user=request.user)
    talent_fav.saved.remove(gig)
    return Response({'message': 'Gig unsaved'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def apply_view(request, id):
    #Check if gig exists
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail':'Gig not found'})
    #Check if user is talent, only talent can apply gig
    if request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail': 'Only talent can apply gig'})
    #Check if gig expired, can't apply expired gig
    if gig.expired_at.date() < timezone.now().date():
        return Response({'detail': 'Can\'t apply expired gig'}, status=status.HTTP_412_PRECONDITION_FAILED)
    user = request.user
    talent_url = BASE_URL + 'talents/' + str(user.id) + '/'
    gig_url = BASE_URL + 'gigs/' + str(gig.id) + '/'
    #Create new notification object to notify gig owner/poster
    Notification.objects.create(
    user=gig.poster, 
    title='New application', 
    message=f'<a href="{talent_url}">{user.username}</a>  has applied your gig <a href="{gig_url}">{gig.title}</a>.')
    
    talent_fav = TalentFav.objects.get(user=user)
    talent_fav.applied.add(gig)
    return Response({'message':'Apply gig successfully'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def withdraw_view(request, id):
    #Check if gig exists
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    #Check if user is talent, only talent can withdraw gig
    if request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail': 'Only talent can apply gig'})
    #Check if gig expired, can't withdraw expired gig
    if gig.expired_at.date() < timezone.now().date():
        return Response({'detail': 'Can\'t withdraw application of expired gig'}, status=status.HTTP_412_PRECONDITION_FAILED)
    talent_fav = TalentFav.objects.get(user=request.user)
    talent_fav.applied.remove(gig)
    return Response({'message':'Withdraw gig successfully'})

#Gig poster close gig without award
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def close_view(request, id):
    #Check if gig exists
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    #Only gig poster can close gig
    if gig.poster != request.user:
        raise exceptions.PermissionDenied({'detail': 'Only gig poster can close gig'})
    #Only can close open gig
    # if (gig.expired_at.date() < timezone.now().date()) or (gig.is_closed):
    #     return Response({'detail': 'Can\'t close expired or already closed gig'}, status=status.HTTP_412_PRECONDITION_FAILED)
    if gig.is_closed:
        return Response({'detail': 'Can\'t close already closed gig'}, status=status.HTTP_412_PRECONDITION_FAILED)

    #Set gig as closed
    gig.is_closed = True
    gig.save()
    
    gig_url = BASE_URL + 'gigs/' + str(gig.id) + '/'
    #Create notification entry for each applicant
    for talent in gig.talent_applied.all():
        Notification.objects.create(user=talent.user, title=f'Gig closed', message=f'Gig <a href="{gig_url}">{gig.title}</a> you applied has been closed without award.')

    return Response({'message': 'Gig is closed'})

#Gig poster award gig to talent
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def award_view(request, id):
    #Check if gig exists
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Git not found'})
    #Only gig poster can award gig
    if gig.poster != request.user:
        raise exceptions.PermissionDenied({'detail': 'Only gig poster can award gig'})
    #Cannot award already fully closed gig or gig expired more than 60 days ago
    if (gig.is_closed) or (gig.expired_at.date() + timedelta(days=60) < timezone.now().date()) :
        return Response({'detail': 'Can\'t award already archived gig or gig expired 60 days ago'}, status=status.HTTP_412_PRECONDITION_FAILED)

    # Check if applicant to be awarded exists
    try:
        winner = User.objects.get(pk=request.data['winner'])
    except:
        raise exceptions.NotFound({'detail': 'Applicant not found'})
    # If user to be award didn't apply the gig
    if winner.is_hirer or winner.talent_fav not in gig.talent_applied.all():
        raise exceptions.NotFound({'detail': 'Applicant didn\'t apply the gig'})

    # Add applicant as winner
    gig.winner = winner
    gig.save()
    
    #Front end url of gig page
    gig_url = BASE_URL + 'gigs/' + str(gig.id) + '/'
    #Send notifications to applicant
    for talent in gig.talent_applied.all():
        if talent.user == winner:
            #send congrat notification to winner
            message = f'Congrats! Gig <a href="{gig_url}">{gig.title}</a> has been awarded to you.'
            title = 'Gig Award'
        else:
            #inform other users about gig awarded other candidate
            title = 'Gig closed'
            message = f'Gig <a href="{gig_url}">{gig.title}</a> has been awarded to other candidate. Fret not, find more suitable gigs at MyGigs recommended tab.'

        Notification.objects.create(user=talent.user, title=title, message=message)
    return Response({'message': 'Gig awarded'})

# Invite talent to apply gig
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def invite_view(request, id):
    # Check if gig or talent exists
    try:
        gig = Gig.objects.get(pk=id)
        #Talent id store in request data talent key
        talent_fav = User.objects.get(pk=request.data['talent']).talent_fav
    except:
        raise exceptions.NotFound({'detail': 'Talent or gig not found.'})
    
    if gig.poster != request.user:
        raise exceptions.PermissionDenied({'detail': 'Only gig poster can invite applicant to the gig'})
    
    #Can't invite talent to closed, expired or already awarded gig
    if (gig.is_closed) or (gig.expired_at.date() < timezone.now().date()) or gig.winner:
        return Response({'detail': 'Can\'t invite talent to closed or expired gig'}, status=status.HTTP_412_PRECONDITION_FAILED)

    #Add gig to TalentFav invited field
    talent_fav.invited.add(gig)

    #Front end url of gig page
    gig_url = BASE_URL + 'gigs/' + str(gig.id) + '/'
    #Send notification to talent
    Notification.objects.create(user=talent_fav.user, title='Gig invite', message=f'Hey, someone take notices of your profile, please heads over to <a href="{gig_url}">{gig.title}</a>')

    return Response({'message': 'Invite success'})

def hirer_view(request, id):
    pass

# Gig poster confirm acceptance of deliverable of gig
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def complete_gig_view(request, id):
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})

    if gig.poster != request.user:
        raise exceptions.PermissionDenied({'detail': 'Only gig poster can confirm gig completion'})

    if gig.winner:
        gig.is_completed = True
        gig.save()
        return Response({'message': 'Gig completion is updated'})
    
    return Response({'detail': 'Only can confirm gig which has been awarded'}, status=status.HTTP_412_PRECONDITION_FAILED)
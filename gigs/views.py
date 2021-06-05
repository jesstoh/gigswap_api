import os
from django.shortcuts import render
from django.core.paginator import Paginator
import json
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
from accounts.models import User, TalentProfile
from talents.models import TalentFav
from notifications.models import Notification

# Get base url of front end 
BASE_URL = os.environ['BASE_URL']
PAGE_ITEMS_COUNT = 10 #set number items to display per page

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def index_view(request):
    if request.method == 'POST':
        if not request.user.is_hirer:
            raise exceptions.PermissionDenied({'detail': 'Only hirer can create gig listing'})

        # Only hirer with completed profile can create gig
        if not request.user.is_profile_complete:
            raise exceptions.PermissionDenied({'details': 'Only hirer with completed profile can create gig'})
        gig = GigSerializer(data=request.data, context={'request':request})
        if gig.is_valid(raise_exception=True):
            gig.save()
        return Response(gig.data, status=status.HTTP_201_CREATED)
        
    if request.method == 'GET':
        query_params = request.GET
        
        if query_params.get('search'):
            #Searching value in gig description
            gigs = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date(), description__icontains=query_params.get('search')).order_by('-created_at')
        elif query_params.get('filter'):
            #process query param 
            is_remote = True if query_params.get('is_remote') =='true' else False
            is_fixed = True if query_params.get('is_fixed') =='true' else False           
            subcategories = json.loads(query_params['subcategories'])
            hour_rate = int(query_params.get('hour_rate'))

            gigs = gigs = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date(),hour_rate__gte=hour_rate)

            if is_remote:
                gigs = gigs.filter(is_remote=True)
            if is_fixed:
                gigs = gigs.filter(is_fixed=True)
            if len(subcategories) > 0:
                gigs = gigs.filter(subcategories__in=set(subcategories))
            gigs = gigs.order_by('-created_at')

        else:
            #No filter or search
            gigs = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date()).order_by('-created_at')

        #Pagination
        gigs_pages = Paginator(gigs, PAGE_ITEMS_COUNT) 

        #set initial default page
        page = 1
        if query_params.get('page'):
            try:
                query_page = int(query_params.get('page'))
            except:
                query_page = 1
            if (1 < query_page <= gigs_pages.num_pages):
                page = query_page

        gigs_paginated = gigs_pages.page(page)
        gigs_serializer = GigSerializer(gigs_paginated, many=True)

        # gigs_serializer = GigSerializer(gigs, many=True)
        # return Response(gigs_serializer.data)
        return Response({'gigs': gigs_serializer.data, 'pageCount': gigs_pages.num_pages})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_gig_view(request):
    user = request.user
    if user.is_hirer or user.is_staff:
        raise exceptions.PermissionDenied({'detail': 'Only talent can view recommended gigs'})
    
    # Only talent with completed profile can find matched gigs
    try:
        talent_profile = TalentProfile.objects.get(user=user)
    except:
        return Response({'detail': 'Please complete your profile to get match gigs'}, status=status.HTTP_412_PRECONDITION_FAILED)

    #Filter active gigs based on talent preference
    gigs = Gig.objects.filter(is_closed=False, winner__isnull=True, expired_at__gt=timezone.now().date(), subcategories__in=set(talent_profile.skills.all()), hour_rate__gte=talent_profile.min_pay, is_fixed=talent_profile.fixed_term)
    #Show only remote gig if talent preference is remote only
    if talent_profile.remote:
        gigs = gigs.filter(is_remote=True)
    gigs_serialized = GigSerializer(gigs, many=True)
    return Response(gigs_serialized.data)

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

    user = request.user
    # Check if user has completed profile, before can apply gig
    if not user.is_profile_complete:
        raise exceptions.PermissionDenied({'detail': 'Only talent with complete profile can apply gig'})

    #Check if gig expired, can't apply expired gig
    if gig.expired_at.date() < timezone.now().date():
        return Response({'detail': 'Can\'t apply expired gig'}, status=status.HTTP_412_PRECONDITION_FAILED)
    
    talent_url = BASE_URL + 'talents/' + str(user.id) + '/'
    # gig_url = BASE_URL + 'gigs/' + str(gig.id) + '/'
    #Create new notification object to notify gig owner/poster
    Notification.objects.create(
    user=gig.poster, 
    title='New application', 
    message=f'Talent {user.username} has applied your gig {gig.title}. Check out talent\'s profile now', link=talent_url)
    
    talent_fav = TalentFav.objects.get(user=user)
    talent_fav.applied.add(gig)
    talent_fav.saved.remove(gig) #remove gig from saved list after applying
    talent_fav.invited.remove(gig) #remove gig from invited list after applying
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
    talent_fav.saved.add(gig) #aAdd gig back to save list after withdraw
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
        Notification.objects.create(user=talent.user, title=f'Gig closed', message=f'Gig {gig.title} you applied has been closed without award.', link=gig_url)

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
            message = f'Congrats! Gig {gig.title} has been awarded to you.'
            title = 'Gig Award'
        else:
            #inform other users about gig awarded other candidate
            title = 'Gig closed'
            message = f'Gig {gig.title} has been awarded to other candidate. Fret not, find more suitable gigs at MyGigs recommended tab.'

        Notification.objects.create(user=talent.user, title=title, message=message, link=gig_url)
        #Remove gigs from talent applied list if it is awarded to the talent
    talent_fav = TalentFav.objects.get(user=winner)
    talent_fav.applied.remove(gig)
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
    Notification.objects.create(user=talent_fav.user, title='Gig invite', message=f'Hey, someone take notices of your profile, please heads over to gig {gig.title}', link=gig_url)

    return Response({'message': 'Invite success'})



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

# Login talent to flag a gig
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def flag_view(request, id):
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    
    # Only can flag active gig
    if gig.expired_at.date() < timezone.now().date() or gig.is_closed or gig.winner:
        return Response({'detail': 'Can\'t flag expired or closed gig'}, status=status.HTTP_412_PRECONDITION_FAILED)
    

    user = request.user
    #Check if login user is a talent
    if user.is_hirer or user.is_staff:
        raise exceptions.PermissionDenied({'detail': 'Only talent can flag a gig'})
    
    #Add user to flag field
    gig.flag.add(user)
    return Response({'message': 'Flag recorded'})

#Login talent to unflag a gig
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def unflag_view(request, id):
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    
    # Only can unflag active gig
    if gig.expired_at.date() < timezone.now().date() or gig.is_closed or gig.winner:
        return Response({'detail': 'Can\'t unflag expired or closed gig'}, status=status.HTTP_412_PRECONDITION_FAILED)
    

    user = request.user
    #Check if login user is a talent
    if user.is_hirer or user.is_staff:
        raise exceptions.PermissionDenied({'detail': 'Only talent can unflag a gig'})
    
    #Remove user from flag field
    gig.flag.remove(user)
    return Response({'message': 'Gig unflagged'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hirer_view(request):
    if not request.user.is_hirer:
        raise exceptions.PermissionDenied({'detail': 'Only hirer can access'})

    gigs = Gig.objects.filter(poster=request.user)
    gigs_serialized = GigSerializer(gigs, many=True)

    return Response(gigs_serialized.data)

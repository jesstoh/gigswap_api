import os
from django.shortcuts import render
from django.db.models import Avg, Count
from django.core.paginator import Paginator
import json
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from accounts.models import User, TalentProfile
from accounts.serializers import TalentProfileSerializer
from talents.serializers import TalentDetailSerializer, TalentFavSerializer
from talents.models import TalentFav
from hirers.models import HirerFav

# Create your views here.
PAGE_ITEMS_COUNT = os.environ['PAGE_ITEMS_COUNT'] #set number items to display per page
# Get all talents profiles


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_index(request):
    user = request.user
    # Only hirers or admin can access list of talents
    if user.is_hirer or user.is_staff:
        query_params = request.GET
        if query_params.get('search'):
            # Searching value in bio
            talents = TalentProfile.objects.filter(
                bio__icontains=query_params.get('search'), user__is_active=True)
        elif query_params.get('filter'):
            # process query param
            skills = json.loads(query_params['skills'])
            rating = int(query_params.get('rating'))
            gigs_won = int(query_params.get('gigs_won'))
            talents_profile_annotated = TalentProfile.objects.annotate(avg_rating=Avg('user__talent_review__rating'), gigs_won_count=Count('user__gigs_won'))
            # talents = talents_profile_annotated.filter(avg_rating__gte=rating)
            if rating > 0:
                talents = talents_profile_annotated.filter(avg_rating__gte=rating)
            else:
                talents = talents_profile_annotated
            if gigs_won > 0:
                talents = talents.filter(gigs_won_count__gte=gigs_won)
            if len(skills) > 0:
                talents = talents.filter(skills__in=skills)
            #Only show active users
            talents = talents.filter(user__is_active=True)
        else:
            talents = TalentProfile.objects.filter(user__is_active=True)
        # talents_serialized = TalentProfileSerializer(talents, many=True)

         #Pagination
        talents_pages = Paginator(talents, PAGE_ITEMS_COUNT) 

        #set initial default page
        page = 1
        if query_params.get('page'):
            try:
                query_page = int(query_params.get('page'))
            except:
                query_page = 1
            if (1 < query_page <= talents_pages.num_pages):
                page = query_page

        talents_paginated = talents_pages.page(page)
        talents_serialized = TalentProfileSerializer(talents_paginated, many=True)

        return Response({'talents':talents_serialized.data, 'pageCount': talents_pages.num_pages})
    else:
        raise exceptions.PermissionDenied(
            {'detail': 'Only hirers or admin can access talents list'})


# Show detail of talent
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_show(request, id):
    # Check if talent exists
    try:
        talent = User.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Talent not found'})
    # Check if talent completed the profile
    if not talent.is_profile_complete:
        raise exceptions.NotFound({'detail': 'Talent profile not found'})

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

# login hirer save talent


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def view_save(request, id):
    # Check if talent and profile exist
    try:
        talent = User.objects.get(pk=id)
        talent_profile = TalentProfile.objects.get(user=talent)
    except:
        raise exceptions.NotFound(
            {'detail': 'Talent or Talent Profile not found'})
    # Check if user hirer, only hirer can save talent
    if not request.user.is_hirer:
        raise exceptions.PermissionDenied(
            {'detail': 'Only hirer can save talent profile'})
    hirer_fav = HirerFav.objects.get(user=request.user)
    hirer_fav.saved.add(talent_profile)
    return Response({'message': 'Talent saved'})

# Login hirer unsave talent profile from HirerFav list


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def view_unsave(request, id):
    # Check if talent and profile exist
    try:
        talent = User.objects.get(pk=id)
        talent_profile = TalentProfile.objects.get(user=talent)
    except:
        raise exceptions.NotFound(
            {'detail': 'Talent or Talent Profile not found'})
    # Check if user hirer, only hirer can unsave talent
    if not request.user.is_hirer:
        raise exceptions.PermissionDenied(
            {'detail': 'Only hirer can unsave talent profile'})
    hirer_fav = HirerFav.objects.get(user=request.user)
    hirer_fav.saved.remove(talent_profile)
    return Response({'message': 'Talent unsaved'})

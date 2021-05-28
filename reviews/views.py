import os
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from reviews.serializers import TalentReviewSerializer, HirerReviewSerializer
from reviews.models import TalentReview, HirerReview
from gigs.models import Gig
from notifications.models import Notification

# Create your views here.

# Get base url of front end 
BASE_URL = os.environ['BASE_URL']

#Review hirer
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_hirer(request):
    gig_id = request.data.get('gig_id')
    #Check if gig_id is send in request data
    if gig_id is None:
        raise exceptions.ValidationError({'detail': 'Gig id is required.'})

    #Check if gig exists   
    try:
        gig = Gig.objects.get(pk=gig_id) 
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
        
    #Only winner can review hirer
    if gig.winner != request.user:
        raise exceptions.PermissionDenied({'detail': 'Only hired talent can review hirer'})

    #Check if review has been created
    if HirerReview.objects.filter(gig=gig).exists():
        return Response({'detail': 'Review already been created, no duplicate review is allowed'}, status=status.HTTP_412_PRECONDITION_FAILED)

    user = request.user
    hirer_review = HirerReviewSerializer(data=request.data, context={'request': request})
    if hirer_review.is_valid(raise_exception=True):
        hirer_review.save() #Create review if valid

        review_url = BASE_URL + 'hirer-review/' + str(hirer_review.data['id']) + '/'
        # talent_url = BASE_URL + 'talents/' + str(user.id) + '/'
        #Create new notification object to notify gig owner/poster
        Notification.objects.create(
        user=gig.poster, 
        title='New review', 
        message=f'Talent {user.username} has provided a review for recently completed gig {gig.title}.', link=review_url)

        return Response(hirer_review.data)

#Review talent
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_talent(request):
    gig_id = request.data.get('gig_id')
    #Check if gig_id is send in request data
    if gig_id is None:
        raise exceptions.ValidationError({'detail': 'Gig id is required.'})

    #Check if gig exists   
    try:
        gig = Gig.objects.get(pk=gig_id) 
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})

    #Only gig poster can review hired talent
    if gig.poster != request.user:
        raise exceptions.PermissionDenied({'detail': 'Only gig poster can review hired talent'})

    #Check if review has been created
    if TalentReview.objects.filter(gig=gig).exists():
        return Response({'detail': 'Review already been created, no duplicate review is allowed'}, status=status.HTTP_412_PRECONDITION_FAILED)

    user = request.user
    talent_review = TalentReviewSerializer(data=request.data, context={'request': request})
    if talent_review.is_valid(raise_exception=True):
        talent_review.save() #Create review if valid

        review_url = BASE_URL + 'talent-review/' + str(talent_review.data['id']) + '/'
        # hirer_url = BASE_URL + 'hirers/' + str(user.id) + '/'
        #Create new notification object to notify talent.
        Notification.objects.create(
        user=gig.winner, 
        title='New review', 
        message=f'Hirer {user.username} has provided a review for recently completed gig {gig.title}.', lind=review_url)

        return Response(talent_review.data)

#Get, edit and delete particular hirer's review
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def hirer_review_show(request, id):
    try:
        review = HirerReview.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Review not found'})

    if request.method == 'GET':
        review_serialized = HirerReviewSerializer(review)
        return Response(review_serialized.data)
    
    #Only review creator or admin can delete review:
    elif request.method == 'DELETE':
        if (request.user != review.talent) and (not request.user.is_staff):
            raise exceptions.PermissionDenied({'detail': 'Only review creator or admin can delete review'})
        review.delete()
        return Response({'message':'Review delete success.'})
    
    elif request.method == 'PUT':
        #Only review creator can edit review
        if request.user != review.talent:
            raise exceptions.PermissionDenied({'detail': 'Only review creator can edit review'})
        
        review = HirerReviewSerializer(instance=review, data=request.data, context={'request':request})
        if review.is_valid(raise_exception=True):
            review.save()
            return Response(review.data)

#Get, edit and delete particular talent's review
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def talent_review_show(request, id):
    try:
        review = TalentReview.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Review not found'})

    if request.method == 'GET':
        review_serialized = TalentReviewSerializer(review)
        return Response(review_serialized.data)

    #Only review creator or admin can delete review:
    elif request.method == 'DELETE':
        if (request.user != review.hirer) and (not request.user.is_staff):
            raise exceptions.PermissionDenied({'detail': 'Only review creator or admin can delete review'})
        review.delete()
        return Response({'message':'Review delete success.'})

    elif request.method == 'PUT':
        #Only review creator can edit review
        if request.user != review.hirer:
            raise exceptions.PermissionDenied({'detail': 'Only review creator can edit review'})
        
        review = TalentReviewSerializer(instance=review, data=request.data, context={'request':request})
        if review.is_valid(raise_exception=True):
            review.save()
            return Response(review.data)
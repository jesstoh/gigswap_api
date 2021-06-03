import os
from django.db.models import Avg, Case, When, Value, IntegerField, Count
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
from accounts.models import User

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
        message=f'Hirer {user.username} has provided a review for recently completed gig {gig.title}.', link=review_url)

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

#Get all review related to hirer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hirer_review_index(request, hirer_id):
    try:
        user = User.objects.get(pk=hirer_id)
    except:
        raise exceptions.NotFound({'detail': 'Hirer not found'})

    # if user id is not for hirer
    if not user.is_hirer:
        raise exceptions.NotFound({'detail': 'Hirer not found'})

    # Get all reviews given by hirer
    give_reviews = TalentReview.objects.filter(hirer=user)
    
    # Get all reviews received by hirer
    hirer_reviews = HirerReview.objects.filter(hirer=user)

    #Annotating boolean field to 0 and 1
    hirer_reviews_annotated = hirer_reviews.annotate(is_ontime=Case(When(payment_ontime=True, then=Value(1)), default=0, output_field=IntegerField()))

    #Get summary of reviews (average)
    summary = hirer_reviews_annotated.aggregate(avg_rating=Avg('rating'), avg_ontime=Avg('is_ontime'), avg_scope=Avg('scope'), review_count=Count('rating'))

    for ele in ['avg_rating', 'avg_ontime', 'avg_scope']:
        if summary[ele] is not None:
            summary[ele] = round(summary[ele], 2)
    hirer_reviews_serialized = HirerReviewSerializer(hirer_reviews, many=True)

    give_reviews_serialized = TalentReviewSerializer(give_reviews, many=True)

    return Response({'summary': summary, 'reviews': hirer_reviews_serialized.data, 'give_reviews': give_reviews_serialized.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def talent_review_index(request, talent_id):
    try:
        talent = User.objects.get(pk=talent_id)
    except:
        raise exceptions.NotFound({'detail': 'Talent not found'})

    # if user id is not for hirer
    if talent.is_hirer or talent.is_staff:
        raise exceptions.NotFound({'detail': 'Talent not found'})

    
    # Get all reviews given by talent
    give_reviews = HirerReview.objects.filter(talent=talent)

    # Get all reviews received by talent
    talent_reviews = TalentReview.objects.filter(talent=talent)

    #Annotating boolean field to 0 and 1
    talent_reviews_annotated = talent_reviews.annotate(ontime=Case(When(is_ontime=True, then=Value(1)), default=0, output_field=IntegerField()), is_recommended=Case(When(recommended=True, then=Value(1)), default=0, output_field=IntegerField()))

    #Get summary of reviews (average)
    summary = talent_reviews_annotated.aggregate(avg_rating=Avg('rating'), avg_ontime=Avg('ontime'), avg_quality=Avg('quality'), avg_recommended=Avg('is_recommended'), review_count=Count('rating'))
    
    talent_reviews_serialized = TalentReviewSerializer(talent_reviews, many=True)
    give_reviews_serialized = HirerReviewSerializer(give_reviews, many=True)

    for ele in ['avg_rating', 'avg_ontime', 'avg_quality', 'avg_recommended']:
        if summary[ele] is not None:
            summary[ele] = round(summary[ele], 2)

    return Response({'summary': summary, 'reviews': talent_reviews_serialized.data, 'give_reviews': give_reviews_serialized.data})
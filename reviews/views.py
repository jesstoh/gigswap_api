from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from reviews.serializers import TalentReviewSerializer, HirerReviewSerializer
from reviews.models import TalentReview, HirerReview
from gigs.models import Gig

# Create your views here.
#Reviewing hirer
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

    hirer_review = HirerReviewSerializer(data=request.data, context={'request': request})
    if hirer_review.is_valid(raise_exception=True):
        hirer_review.save() #Create review if valid
        return Response(hirer_review.data)

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

    talent_review = TalentReviewSerializer(data=request.data, context={'request': request})
    if talent_review.is_valid(raise_exception=True):
        talent_review.save() #Create review if valid
        return Response(talent_review.data)

def hirer_review_show(request, id):
    pass


def talent_review_show(request, id):
    pass
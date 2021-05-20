from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import exceptions
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from gigs.models import Gig
from categories.models import Subcategory
from gigs.serializers import GigSerializer
from accounts.models import User

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
    try:
        gig = Gig.objects.get(pk=id)
    except:
        raise exceptions.NotFound({'detail': 'Gig not found'})
    
    
def unsave_view(request, id):
    pass

def apply_view(request, id):
    pass

def withdraw_view(request, id):
    pass

def close_view(request, id):
    pass

def award_view(request, id):
    pass

def invite_view(request, id):
    pass

def hirer_view(request, id):
    pass


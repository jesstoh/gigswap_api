from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response 
from rest_framework import exceptions
from rest_framework import status
from gigs.models import Gig
from categories.models import Subcategory
from gigs.serializers import GigSerializer
from accounts.models import User

# Create your views here.
@api_view(['GET', 'POST'])
def index_view(request):
    if request.method == 'POST':
        gig = GigSerializer(data=request.data)
        if gig.is_valid(raise_exception=True):
            gig.save()
        return Response(gig.data, status=status.HTTP_201_CREATED)
    if request.method == 'GET':
        gigs = Gig.objects.all()
        gigs_serializer = GigSerializer(gigs, many=True)
        return Response(gigs_serializer.data)

def recommend_gig_view(request):
    pass

def show_view(request, id):
    pass

def save_view(request, id):
    pass

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


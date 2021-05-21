import os
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from gigs.models import Gig


# Create your views here.

# Get base url of front end 
BASE_URL = os.environ['BASE_URL']

#Get and create notifications
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def view_index(request):
    if request.method == 'GET':
        notifications = Notification.objects.filter(user=request.user)
        notifications_serialized = NotificationSerializer(notifications, many=True)
        return Response(notifications_serialized.data)
    
    # Bulk delete of notifications by user
    elif request.GET.get('action') == 'delete' and request.method == 'POST':
        try:
            #Get notification id to be deleted store in request data
            notifications_ids = request.data.get('notification_id')
            #Filter and delete notifications, only user can delete own notifications
            notifications = Notification.objects.filter(id__in=notifications_ids, user=request.user)
            if notifications:
                return Response({'message': 'Delete success'})
            else:
                return Response({'message': 'No notification delete'})
        except:
            raise exceptions.ValidationError({'detail':'Please provide valid notifications id'})


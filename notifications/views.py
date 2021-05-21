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

    elif request.method == 'POST':
        try:
            title = request.data['title']
            gig = Gig.objects.get(pk=request.data['gig_id'])
        except:
            raise exceptions.NotFound({'detail': 'Gig not found'})

        if gig.winner != request.user:
            raise exceptions.PermissionDenied({'detail': 'Only gig winner can request for payment or acceptance'})
        
        gig_url = BASE_URL + 'gigs/' + str(gig.id) + '/'
        if title == 'Request for pay':
            #Request of payment by talent
            Notification.objects.create(user=gig.poster, title=title, message=f'Talent {request.user.username} has requested payment for gig <a href="{gig_url}">{gig.title}</a>'
            )
            return Response({'message': 'Payment requested'})
            
        elif title == 'Request for acceptance':
            #Request of gig deliverable acceptance 
            Notification.objects.create(user=gig.poster, title=title, message=f'Talent {request.user.username} has requested acceptance of deliverable for gig <a href="{gig_url}">{gig.title}</a>'
            )
            return Response({'message': 'Gig deliverable acceptance requested'})
        raise exceptions.ValidationError({'detail': 'Please provide valid notification request type'})


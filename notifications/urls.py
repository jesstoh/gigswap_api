from django.urls import path
from notifications.views import *

app_name = "notifications"

urlpatterns = [
    path('', view_index, name='notification_index'),
    path('read/', view_read, name='read_notification')
]

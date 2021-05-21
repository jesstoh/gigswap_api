from django.urls import path
from talents.views import *

urlpatterns = [
    path('', view_index, name='talents_index')
]
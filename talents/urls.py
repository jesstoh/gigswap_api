from django.urls import path
from talents.views import *

urlpatterns = [
    path('', view_index, name='talents_index'),
    path('<int:id>/', view_show, name='talent_show')
]
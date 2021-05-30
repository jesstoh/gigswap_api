from django.urls import path
from hirers.views import *

urlpatterns = [
    path('fav/', view_index, name='hirer_fav'),
    path('<int:id>/', view_show, name='hirer_show')
]
from django.urls import path
from hirers.views import *

urlpatterns = [
    path('fav/', index_view, name='hirer_fav')
]
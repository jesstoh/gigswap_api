from django.urls import path
from reviews.views import *

app_name = "reviews"

urlpatterns = [
    path('hirer/', review_hirer, name='review_hirer'),
    path('talent/', review_talent, name='review_talent'),
    path('hirer/<uuid:id>/', hirer_review_show, name='show_review_hirer'),
    path('talent/<uuid:id>/', talent_review_show, name='show_review_talent'),
    path('hirer/all/<int:hirer_id>/', hirer_review_index, name='hirer_review_index') #Get all reviews related to hirer
]
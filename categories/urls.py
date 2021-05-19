from django.urls import path
from categories.views import *

app_name = 'categories'

urlpatterns = [
    path('', categories_index, name='categories_index'),
    path('sub/', subcat_index, name='subcat_index'),
    path('<uuid:id>/', categories_show, name='show_category'),
    path('sub/<uuid:id>/', subcat_show, name='show_subcat')
]
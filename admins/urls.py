from django.urls import path
from admins.views import *

urlpatterns = [
    path('dashboard/', dashboard_view, name='admins_dashboard'), #Get summary of app
    path('users/', users_view, name='users_index') #Get all users
]


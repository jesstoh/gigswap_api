from django.urls import path
from admins.views import *

urlpatterns = [
    path('dashboard/', dashboard_view, name='admins_dashboard'), #Get summary of app
    path('users/', users_view, name='users_index'), #Get all users
    path('users/<int:userId>/deactivate/', deactivate_view, name='deactivate_user'), #Deactivate user
    path('users/<int:userId>/activate/', activate_view, name='activate_user'), #activate user
    path('gigs/', gigs_index_view, name='gigs_index')
]


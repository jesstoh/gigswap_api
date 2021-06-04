from django.urls import path
from admins.views import *

urlpatterns = [
    path('dashboard/', dashboard_view, name='admins_dashboard')
]


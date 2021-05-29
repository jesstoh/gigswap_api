from django.urls import path
from talents.views import *

urlpatterns = [
    path('', view_index, name='talents_index'),
    path('<int:id>/', view_show, name='talent_show'),
    path('fav/', view_fav, name='talent_fav'),
    path('<int:id>/save/', view_save, name='save_talent'),
    path('<int:id>/unsave/', view_unsave, name='unsave_talent')
]
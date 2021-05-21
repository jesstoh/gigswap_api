from django.urls import path
from gigs.views import *


urlpatterns = [
    path('', index_view, name='gigs_index'),
    path('recommended/', recommend_gig_view, name="recommend_gig"),
    path('<uuid:id>/', show_view, name='show_gig'),
    path('<uuid:id>/save/', save_view, name='save_gig'),
    path('<uuid:id>/unsave/', unsave_view, name='unsave_gig'),
    path('<uuid:id>/apply/', apply_view, name='apply_gig'),
    path('<uuid:id>/withdraw/', withdraw_view, name='withdraw_gig'),
    path('<uuid:id>/close/', close_view, name='close_gig'),
    path('<uuid:id>/award/', award_view, name='award_gig'),
    path('<uuid:id>/invite/', invite_view, name='invite_talent'),
    path('<uuid:id>/complete/', complete_gig_view, name='gig_complete'),
    path('hirer/', hirer_view, name='hirer_gigs_index')

]
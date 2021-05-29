from rest_framework import serializers
from django.utils import timezone
from hirers.models import HirerFav
from gigs.models import Gig
from accounts.serializers import UserSerializer, TalentProfileSerializer
from gigs.serializers import GigSerializer

class HirerFavSerializer(serializers.ModelSerializer):
    hired_talents = serializers.SerializerMethodField('hired_talents_list')
    saved = TalentProfileSerializer(read_only=True, many=True)
    active_gigs = serializers.SerializerMethodField('gigs_active')
    pending_award_gigs = serializers.SerializerMethodField('gigs_pending_award')
    awarded_gigs = serializers.SerializerMethodField('gigs_awarded')
    not_paid_gigs = serializers.SerializerMethodField('gigs_not_paid') #gigs completed by not paid yet
    completed_gigs = serializers.SerializerMethodField('gigs_completed') #gigs completed with payment 
    closed_gigs = serializers.SerializerMethodField('gigs_closed') #gigs closed without award


    #Get active gigs
    def gigs_active(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, expired_at__gte=timezone.now().date(), is_closed=False, winner__isnull=True)
        return GigSerializer(gigs, many=True).data

    # Expired gigs pending award
    def gigs_pending_award(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, expired_at__lt=timezone.now().date(), is_closed=False, winner__isnull=True)
        return GigSerializer(gigs, many=True).data

    # Awarded gigs
    def gigs_awarded(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, winner__isnull=False, is_completed=False, paid=False)
        return GigSerializer(gigs, many=True).data
    
    #Gigs pending payment
    def gigs_not_paid(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, winner__isnull=False, is_completed=True, paid=False)
        return GigSerializer(gigs, many=True).data

    #Gigs completed with payment
    def gigs_completed(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, winner__isnull=False, is_completed=True, paid=True)
        return GigSerializer(gigs, many=True).data

    #Gigs closed without award
    def gigs_closed(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, is_closed=True)
        return GigSerializer(gigs, many=True).data

    #Get set of winners from hirer's gigs
    def hired_talents_list(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, winner__isnull=False)
        winners = set(gig.winner.talent_profile for gig in gigs)
        winners = TalentProfileSerializer(winners, many=True)
        # winners = UserSerializer(winners, many=True)
        return winners.data
        
    
    class Meta:
        model = HirerFav
        fields = '__all__'
    
    


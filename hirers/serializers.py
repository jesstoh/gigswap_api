from rest_framework import serializers
from django.db.models import Avg
from django.utils import timezone
from accounts.models import User
from hirers.models import HirerFav
from gigs.models import Gig
from accounts.serializers import UserSerializer, TalentProfileSerializer, HirerProfileSerializer
from gigs.serializers import GigSerializer
from reviews.models import HirerReview

class HirerFavSerializer(serializers.ModelSerializer):
    hired_talents = serializers.SerializerMethodField('hired_talents_list')
    saved = TalentProfileSerializer(read_only=True, many=True)
    active_gigs = serializers.SerializerMethodField('gigs_active')
    pending_award_gigs = serializers.SerializerMethodField('gigs_pending_award')
    awarded_gigs = serializers.SerializerMethodField('gigs_awarded')
    not_paid_gigs = serializers.SerializerMethodField('gigs_not_paid') #gigs completed by not paid yet
    completed_gigs = serializers.SerializerMethodField('gigs_completed') #gigs completed with payment 
    closed_gigs = serializers.SerializerMethodField('gigs_closed') #gigs closed without award
    # Will remove this once implement adapter in React
    saved_talents_list = serializers.SerializerMethodField('get_saved_list')


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

    #Get saved talents in list
    def get_saved_list(self, obj):
        return obj.saved.all().values_list('id', flat=True)

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
    


class HirerDetailSerializer(serializers.ModelSerializer):
    hirer_profile = HirerProfileSerializer(read_only=True)
    active_gigs = serializers.SerializerMethodField('gigs_active')
    review_count = serializers.SerializerMethodField('get_review_count')
    avg_review_rating = serializers.SerializerMethodField('get_review_rating')

    #Get active gigs
    def gigs_active(self, obj):
        gigs = Gig.objects.filter(poster=obj, expired_at__gte=timezone.now().date(), is_closed=False, winner__isnull=True).order_by('-created_at')
        return GigSerializer(gigs, many=True).data
    
    #Get number of reviews received
    def get_review_count(self, obj):
        return HirerReview.objects.filter(hirer=obj).count()

    #Get average review rating
    def get_review_rating(self, obj):
        return HirerReview.objects.filter(hirer=obj).aggregate(Avg('rating'))['rating__avg']

    class Meta:
        model = User
        # fields = "__all__"
        fields = ('id', 'hirer_profile', 
                  'username', 'first_name', 'last_name', 'email', 'active_gigs','review_count', 'avg_review_rating')
        read_only_fields = ('id',)
    


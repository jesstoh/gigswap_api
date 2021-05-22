from rest_framework import serializers
from hirers.models import HirerFav
from gigs.models import Gig
from accounts.serializers import UserSerializer, TalentProfileSerializer

class HirerFavSerializer(serializers.ModelSerializer):
    hired_talents = serializers.SerializerMethodField('hired_talents_list')
    saved = TalentProfileSerializer(read_only=True, many=True)

    #Get set of winners from hirer's gigs
    def hired_talents_list(self, obj):
        gigs = Gig.objects.filter(poster=obj.user, winner__isnull=False)
        winners = set(gig.winner.talent_profile for gig in gigs)
        winners = TalentProfileSerializer(winners, many=True)
        # winners = UserSerializer(winners, many=True)
        return winners.data
        
    
    class Meta:
        model = HirerFav
        fields = ('user','saved', 'hired_talents')
    
    


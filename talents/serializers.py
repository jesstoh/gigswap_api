from rest_framework import serializers
from talents.models import TalentFav
from accounts.serializers import UserSerializer, TalentProfileSerializer
from accounts.models import User, TalentProfile
from gigs.models import Gig
from gigs.serializers import GigSerializer

class TalentDetailSerializer(serializers.ModelSerializer):
    talent_profile = TalentProfileSerializer(read_only=True)
    gigs_won = GigSerializer(read_only=True, many=True)
     
    class Meta:
        model = User
        fields =  "__all__"
        fields = ('id', 'talent_profile', 'gigs_won', 'username', 'first_name', 'last_name', 'email')



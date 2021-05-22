from rest_framework import serializers
from reviews.models import TalentReview, HirerReview
from accounts.serializers import UserSerializer
from gigs.serializers import GigSerializer
from gigs.models import Gig

class TalentReviewSerializer(serializers.ModelSerializer):
    hirer = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)

    class Meta:
        model = TalentReview
        fields = ('gig', 'hirer', 'rating', 'is_ontime', 'quality', 'recommended', 'description', 'created_at')
        read_only_fields = ('hirer', 'created_at', 'gig,')

    def create(self, validated_data):
        request = self.context.get('request')
        gig = Gig.objects.get(id=validated_data['gig_id'])
        hirer = request.user
        talent = gig.winner
        talent_review = TalentReview.objects.create(**validated_data, gig=gig, talent=talent, hirer=hirer)
        return talent_review
 

class HirerReviewSerializer(serializers.ModelSerializer):
    talent = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)

    class Meta:
        model = HirerReview
        fields = ('gig', 'talent', 'rating', 'payment_ontime', 'scope', 'description', 'created_at')
        read_only_fields = ('gig', 'talent', 'created_at', 'gig,')

    def create(self, validated_data):
        request = self.context.get('request')
        gig = Gig.objects.get(id=request.data.get('gig_id'))
        talent = request.user 
        hirer_review = HirerReview.objects.create(**validated_data, gig=gig, talent=talent, hirer=gig.poster)
        return hirer_review
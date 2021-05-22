from rest_framework import serializers
from reviews.models import TalentReview, HirerReview
from accounts.serializers import UserSerializer
from gigs.serializers import GigSerializer

class TalentReviewSerializer(serializers.ModelSerializer):
    hirer = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)

    class Meta:
        model = TalentReview
        fields = ('gig', 'hirer', 'rating', 'is_ontime', 'quality', 'recommended', 'description', 'created_at')


class HirerReviewSerializer(serializers.ModelSerializer):
    talent = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)

    class Meta:
        model = HirerReview
        fields = ('gig', 'talent', 'rating', 'payment_ontime', 'scope', 'description', 'created_at')
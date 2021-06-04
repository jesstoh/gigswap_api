from rest_framework import serializers
from reviews.models import TalentReview, HirerReview
from accounts.serializers import UserSerializer, HirerProfile
from gigs.serializers import GigSerializer
from gigs.models import Gig

class TalentReviewSerializer(serializers.ModelSerializer):
    hirer = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)
    company = serializers.SerializerMethodField('get_company_detail')
    talent_detail = serializers.SerializerMethodField('get_talent_detail')

    def get_company_detail(self, obj):
        return obj.hirer.hirer_profile.company

    def get_talent_detail(self, obj):
        return {'id': obj.talent.id, 'first_name': obj.talent.first_name, 'last_name': obj.talent.last_name}

    class Meta:
        model = TalentReview
        fields = ('id','gig', 'hirer', 'company', 'talent_detail', 'rating', 'is_ontime', 'quality', 'recommended', 'description', 'created_at',)
        read_only_fields = ('id','hirer', 'created_at', 'gig',)

    def create(self, validated_data):
        request = self.context.get('request')
        gig = Gig.objects.get(id=request.data.get('gig_id'))
        hirer = request.user
        talent = gig.winner
        talent_review = TalentReview.objects.create(**validated_data, gig=gig, talent=talent, hirer=hirer)
        return talent_review
 

class HirerReviewSerializer(serializers.ModelSerializer):
    talent = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)
    company = serializers.SerializerMethodField('get_company_detail')

    def get_company_detail(self, obj):
        return obj.hirer.hirer_profile.company

    class Meta:
        model = HirerReview
        fields = ('id','gig', 'talent', 'rating', 'payment_ontime', 'scope', 'description', 'created_at', 'company', 'hirer')
        read_only_fields = ('id', 'gig', 'talent', 'created_at', 'hirer')

    def create(self, validated_data):
        request = self.context.get('request')
        gig = Gig.objects.get(id=request.data.get('gig_id'))
        talent = request.user 
        hirer_review = HirerReview.objects.create(**validated_data, gig=gig, talent=talent, hirer=gig.poster)
        return hirer_review

    # def update(self, instance, validated_data):
    #     request = self.context.get('request')
        
    #     gig = Gig.objects.get(id=request.data.get('gig_id'))
    #     talent = request.user 
    #     hirer_review = HirerReview.objects.create(**validated_data, gig=gig, talent=talent, hirer=gig.poster)
    #     return hirer_review
from rest_framework import serializers
from gigs.models import Gig
from categories.serializers import SubcategorySerializer
from categories.models import Subcategory
from accounts.models import User, HirerProfile, TalentProfile
from accounts.serializers import UserSerializer, HirerProfileSerializer, TalentProfileSerializer
from talents.models import TalentFav
from reviews.models import HirerReview, TalentReview


class GigSerializer(serializers.ModelSerializer):
    # poster = UserSerializer(read_only=True, many=False)
    winner = UserSerializer(read_only=True, many=False)
    subcategories = SubcategorySerializer(read_only=True, many=True)
    applicants = serializers.SerializerMethodField('get_applicants')
    poster_profile = serializers.SerializerMethodField('get_hirer_profile')
    is_hirer_reviewed = serializers.SerializerMethodField('get_hirer_review')
    is_talent_reviewed = serializers.SerializerMethodField('get_talent_review')

    # Get applicant id in a list and flatten into a list
    def get_applicants(self, obj):
        # applicants = obj.talent_applied.all().values_list('user__id', flat=True)
        applicant_ids = obj.talent_applied.all().values_list('user__id', flat=True)
        applicant_profiles = TalentProfile.objects.filter(
            user__in=applicant_ids)
        return TalentProfileSerializer(applicant_profiles, many=True).data

    def get_hirer_profile(self, obj):
        return HirerProfileSerializer(obj.poster.hirer_profile).data
        # return obj.poster.hirer_profile.company

    def get_hirer_review(self, obj):
        return HirerReview.objects.filter(gig=obj).exists()

    def get_talent_review(self, obj):
        return TalentReview.objects.filter(gig=obj).exists()
        
    class Meta:
        model = Gig
        fields = "__all__"
        read_only_fields = ('id', 'poster', 'flag')

    def create(self, validated_data):
        request = self.context.get('request')
        gig = Gig.objects.create(**validated_data, poster=request.user)
        subcat_data = request.data['subcategories']
        # gig = super().create(validated_data, poster=request.user)
        subcategories = []
        # for data in subcat_data:
        #     subcat_id = data['id']
        #     subcat = Subcategory.objects.get(pk=subcat_id)
        #     subcategories.append(subcat)
        for subcat_id in subcat_data:
            # subcat_id = data['id']
            subcat = Subcategory.objects.get(pk=subcat_id)
            subcategories.append(subcat)
        gig.subcategories.add(*subcategories)
        return gig

    def update(self, instance, validated_data):
        gig = super().update(instance, validated_data)
        request = self.context.get('request')
        subcat_data = request.data['subcategories']
        # gig = super().create(validated_data, poster=request.user)
        subcategories = []
        for subcat_id in subcat_data:
            # subcat_id = data['id']
            subcat = Subcategory.objects.get(pk=subcat_id)
            subcategories.append(subcat)
        gig.subcategories.set(subcategories)
        return gig

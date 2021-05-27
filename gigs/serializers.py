from rest_framework import serializers
from gigs.models import Gig
from categories.serializers import SubcategorySerializer
from categories.models import Subcategory
from accounts.models import User, HirerProfile
from accounts.serializers import UserSerializer, HirerProfileSerializer
from talents.models import TalentFav

class GigSerializer(serializers.ModelSerializer):
    # poster = UserSerializer(read_only=True, many=False)
    winner = UserSerializer(read_only=True, many=False)
    subcategories = SubcategorySerializer(read_only=True, many=True)
    applicants = serializers.SerializerMethodField('get_applicants')
    poster_profile = serializers.SerializerMethodField('get_hirer_profile')

    #Get applicant id in a list and flatten into a list
    def get_applicants(self, obj):
        applicants = obj.talent_applied.all().values_list('user__id', flat=True)
        return applicants
    
    def get_hirer_profile(self, obj):       
        return HirerProfileSerializer(obj.poster.hirer_profile).data
        # return obj.poster.hirer_profile.company

    class Meta:
        model = Gig
        fields = "__all__"
        read_only_fields = ('id', 'poster',)
        

    def create(self, validated_data):
        request = self.context.get('request')
        gig = Gig.objects.create(**validated_data, poster=request.user)
        subcat_data = request.data['subcategories']
        # gig = super().create(validated_data, poster=request.user)
        subcategories = []
        for data in subcat_data:
            subcat_id = data['id']
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
        for data in subcat_data:
            subcat_id = data['id']
            subcat = Subcategory.objects.get(pk=subcat_id)
            subcategories.append(subcat)
        gig.subcategories.add(*subcategories)
        return gig

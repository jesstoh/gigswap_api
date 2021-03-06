from rest_framework import serializers
from django.db.models import Avg
from accounts.models import User, TalentProfile, HirerProfile
from categories.serializers import SubcategorySerializer
from categories.models import Subcategory
from gigs.models import Gig
from reviews.models import TalentReview

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'username', 'email', 'password', 'is_hirer', 'is_staff', 'is_active', 'is_profile_complete', 'date_joined']
        read_only_fields = ('id', 'is_staff', 'is_active','is_profile_complete', 'date_joined',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class TalentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SubcategorySerializer(read_only=True, many=True)
    gigs_won = serializers.SerializerMethodField('gigs_won_count') #Quantity of Gig won
    review_count = serializers.SerializerMethodField('get_review_count')
    avg_review_rating = serializers.SerializerMethodField('get_review_rating')

    #Get set of won gigs
    def gigs_won_count(self, obj):        
        return Gig.objects.filter(winner=obj.user).count()

    #Get number of reviews received
    def get_review_count(self, obj):
        return TalentReview.objects.filter(talent=obj.user).count()

     #Get average review rating
    def get_review_rating(self, obj):
        avg_rating = TalentReview.objects.filter(talent=obj.user).aggregate(Avg('rating'))['rating__avg']
        if avg_rating is not None:
            avg_rating = round(avg_rating, 1)
        return avg_rating

    class Meta:
        model = TalentProfile
        fields = '__all__'
        # fields = ['id', 'user', 'bio', 'remote', 'fixed_term', 'skills','image']
        read_only_fields = ('id', 'user')

    def create(self, validated_data):
        request = self.context.get('request')
        profile = TalentProfile.objects.create(**validated_data, user=request.user)
        skill_data = request.data['skills']
        skills = []
        # for data in skill_data:
        #     skill_id = data['id']
        #     skill = Subcategory.objects.get(pk=skill_id)
        #     skills.append(skill)
        for skill_id in skill_data:
            # skill_id = data['id']
            skill = Subcategory.objects.get(pk=skill_id)
            skills.append(skill)
        profile.skills.add(*skills)
        return profile

    def update(self, instance, validated_data):
        profile = super().update(instance, validated_data)
        request = self.context.get('request')
        skill_data = request.data['skills']
        skills = []
        for skill_id in skill_data:
            # skill_id = data['id']
            skill = Subcategory.objects.get(pk=skill_id)
            skills.append(skill)
        profile.skills.set(skills)
        return profile

class HirerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = HirerProfile
        fields = "__all__"
        read_only_fields = ('id', 'user',)

    def create(self, validated_data):
        request = self.context.get('request')
        profile = HirerProfile.objects.create(**validated_data, user=request.user)    
        return profile
  




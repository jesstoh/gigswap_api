from rest_framework import serializers
from django.db.models import Avg
from talents.models import TalentFav
from accounts.serializers import UserSerializer, TalentProfileSerializer
from accounts.models import User, TalentProfile
from gigs.models import Gig
from gigs.serializers import GigSerializer
from reviews.models import TalentReview


class TalentDetailSerializer(serializers.ModelSerializer):
    talent_profile = TalentProfileSerializer(read_only=True)
    gigs_won = GigSerializer(read_only=True, many=True)
    review_count = serializers.SerializerMethodField('get_review_count')
    avg_review_rating = serializers.SerializerMethodField('get_review_rating')

    #Get number of reviews received
    def get_review_count(self, obj):
        return TalentReview.objects.filter(talent=obj).count()

     #Get average review rating
    def get_review_rating(self, obj):
        avg_rating = TalentReview.objects.filter(talent=obj).aggregate(Avg('rating'))['rating__avg']
        if avg_rating is not None:
            avg_rating = round(avg_rating, 1)
        return avg_rating

    class Meta:
        model = User
        # fields = "__all__"
        fields = ('id', 'talent_profile', 'gigs_won',
                  'username', 'first_name', 'last_name', 'email', 'review_count', 'avg_review_rating')


class TalentFavSerializer(serializers.ModelSerializer):
    saved = GigSerializer(read_only=True, many=True)
    applied = GigSerializer(read_only=True, many=True)
    invited = GigSerializer(read_only=True, many=True)
    won = serializers.SerializerMethodField('gigs_won')
    completed = serializers.SerializerMethodField('gigs_completed')
    not_paid = serializers.SerializerMethodField('gigs_not_paid')
    in_progress = serializers.SerializerMethodField('gigs_in_progress')
    # Will remove these two once React using adapter
    saved_list = serializers.SerializerMethodField('get_saved_list')
    applied_list = serializers.SerializerMethodField('get_applied_list')

    # Get won gigs
    def gigs_won(self, obj):
        gigs = Gig.objects.filter(winner=obj.user)
        return GigSerializer(gigs, many=True).data

    # Get list of gig completed and paid
    def gigs_completed(self, obj):
        gigs = Gig.objects.filter(
            winner=obj.user, paid=True, is_completed=True)
        return GigSerializer(gigs, many=True).data

    # Get list of gig job done by not paid
    def gigs_not_paid(self, obj):
        gigs = Gig.objects.filter(
            winner=obj.user, paid=False, is_completed=True)
        return GigSerializer(gigs, many=True).data

    # Get list of gig won but not complete and not paid
    def gigs_in_progress(self, obj):
        gigs = Gig.objects.filter(
            winner=obj.user, paid=False, is_completed=False)
        return GigSerializer(gigs, many=True).data

    def get_saved_list(self, obj):
        return obj.saved.all().values_list('id', flat=True)

    def get_applied_list(self, obj):
        return obj.applied.all().values_list('id', flat=True)

    class Meta:
        model = TalentFav
        # fields = '__all__'
        # fields = ('user', 'saved', 'applied', 'invited', 'won')
        exclude = ('id', 'user',)

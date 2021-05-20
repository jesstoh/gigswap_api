from rest_framework import serializers
from gigs.models import Gig
from categories.serializers import SubcategorySerializer
from categories.models import Subcategory
from accounts.models import User
from accounts.serializers import UserSerializer

class GigSerializer(serializers.ModelSerializer):
    # poster = UserSerializer(read_only=True, many=False)
    # winner = UserSerializer(read_only=True, many=False)
    # subcategories = SubcategorySerializer(read_only=True, many=True)

    class Meta:
        model = Gig
        fields = "__all__"
        read_only_fields = ('id',)

    def create(self, validated_data):
        subcat_data = validated_data.pop('subcategories')
        # user = User.objects.get(pk=user_data)
        gig = Gig.objects.create(**validated_data)
        subcategories = []
        for subcat in subcat_data:
            # subcat_id = subcat.get('id')
            # subcategory = Subcategory.objects.get(pk=subcat)
            subcategories.append(subcat)
        gig.subcategories.add(*subcategories)
        return gig


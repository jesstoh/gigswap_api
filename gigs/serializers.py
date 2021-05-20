from rest_framework import serializers
from gigs.models import Gig
from categories.serializers import SubcategorySerializer
from categories.models import Subcategory
from accounts.models import User
from accounts.serializers import UserSerializer

class GigSerializer(serializers.ModelSerializer):
    poster = UserSerializer(read_only=True, many=False)
    winner = UserSerializer(read_only=True, many=False)
    subcategories = SubcategorySerializer(read_only=True, many=True)

    class Meta:
        model = Gig
        fields = "__all__"
        read_only_fields = ('id',)

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
        return gig


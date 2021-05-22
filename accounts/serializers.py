from rest_framework import serializers
from accounts.models import User, TalentProfile
from categories.serializers import SubcategorySerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'username', 'email', 'password', 'is_hirer', 'is_staff', 'is_active', 'is_profile_complete']
        read_only_fields = ('id', 'is_staff', 'is_active','is_profile_complete')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class TalentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skill = SubcategorySerializer(read_only=True, many=True)
    class Meta:
        model = TalentProfile
        fields = ['id', 'user', 'bio', 'remote', 'fixed_term', 'skill','image']





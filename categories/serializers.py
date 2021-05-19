from rest_framework import serializers
from categories.models import Category, Subcategory

class SubcategorySerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = Subcategory
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(read_only=True, many=True)
    # subcategories = serializers.StringRelatedField(many=True)
    class Meta:
        model = Category
        fields = ('id','name', 'subcategories')
        read_only_fields = ('subcategories',)


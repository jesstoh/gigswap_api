from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import exceptions
from categories.models import Category, Subcategory
from categories.serializers import CategorySerializer, SubcategorySerializer

# Create your views here.
@api_view(['GET', 'POST'])
def categories_index(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        cat_serializers = CategorySerializer(categories, many=True)
        return Response(cat_serializers.data)
    elif request.method == 'POST':
        category = CategorySerializer(data=request.data)
        if category.is_valid(raise_exception=True):
            category.save()
            return Response(category.data)

def subcat_index(request):
    pass

def categories_show(request, id):
    pass

def subcat_show(request, id):
    pass
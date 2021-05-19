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
        cat_serializer = CategorySerializer(categories, many=True)
        return Response(cat_serializer.data)
    elif request.method == 'POST':
        category = CategorySerializer(data=request.data)
        if category.is_valid(raise_exception=True):
            category.save()
            return Response(category.data)

@api_view(['GET', 'POST'])
def subcat_index(request):
    #Get all subcategories
    if request.method == 'GET':
        subcats = Subcategory.objects.all()
        subcats_serializer = SubcategorySerializer(subcats, many=True)
        return Response(subcats_serializer.data)
    #Create new subcategories
    elif request.method == 'POST':
        #Get category id from request post data
        cat_id = request.data.get('category')
        if cat_id is None:
            raise exceptions.ValidationError({'details': 'category id missing'})
        try:
            category = Category.objects.get(pk=cat_id)
            subcat = Subcategory.objects.create(name=request.data.get('name'), category=category)
            subcats_serializer = SubcategorySerializer(subcat)
            return Response(subcats_serializer.data)
        except:
            raise exceptions.ValidationError({'details':'input not valid'})


def categories_show(request, id):
    pass

def subcat_show(request, id):
    pass
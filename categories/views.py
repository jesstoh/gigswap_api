from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status

from categories.models import Category, Subcategory
from categories.serializers import CategorySerializer, SubcategorySerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categories_index(request):
    if request.method == 'GET':
        categories = Category.objects.all().order_by('name')
        cat_serializer = CategorySerializer(categories, many=True)
        return Response(cat_serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def categories_create(request):
    category = CategorySerializer(data=request.data)
    if category.is_valid(raise_exception=True):
        category.save()
        return Response(category.data, status=status.HTTP_201_CREATED)

# Authenticated user can view subcategories
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subcat_index(request):
    #Get all subcategories
    if request.method == 'GET':
        subcats = Subcategory.objects.all().order_by('name')
        subcats_serializer = SubcategorySerializer(subcats, many=True)
        return Response(subcats_serializer.data)

# Only admin can create new subcategory
@api_view(['POST'])
@permission_classes([IsAdminUser])
def subcat_create(request):
    #Create new subcategories
    if request.method == 'POST':
        #Get category id from request post data
        cat_id = request.data.get('category')
        if cat_id is None:
            raise exceptions.ValidationError({'detail': 'category id missing'})
        try:
            category = Category.objects.get(pk=cat_id)
            subcat = Subcategory.objects.create(name=request.data.get('name'), category=category)
            subcats_serializer = SubcategorySerializer(subcat)
            return Response(subcats_serializer.data)
        except:
            raise exceptions.ValidationError({'detail':'input not valid'})

#Get, update and delete particular category by id
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def categories_show(request, id):
    try:
        category = Category.objects.get(pk=id)
    except:
        #Error if category id not found
        raise exceptions.NotFound({'detail': 'Category not found'})

    if request.method == 'DELETE':
        category.delete()
        return Response({'message': 'Delete success'})
    elif request.method == 'PUT':
        cat_serializer = CategorySerializer(instance=category, data=request.data)
        if cat_serializer.is_valid(raise_exception=True):
            cat_serializer.save()
    elif request.method == 'GET':
        cat_serializer = CategorySerializer(category)

    return Response(cat_serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def subcat_show(request, id):
    try:
        subcat = Subcategory.objects.get(pk=id)
    except:
        #Error if category id not found
        raise exceptions.NotFound({'detail': 'Subcategory not found'})

    if request.method == 'DELETE':
        subcat.delete()
        return Response({'message': 'Delete success'})
    elif request.method == 'PUT':               
        try:
            category = Category.objects.get(pk=request.data.get('category'))
            subcat.category = category
            subcat.name = request.data.get("name")
            subcat.save()
        except:
            raise exceptions.ValidationError({'detail': 'Invalid input'})
        subcat_serializer = SubcategorySerializer(subcat)
    elif request.method == 'GET':
        subcat_serializer = SubcategorySerializer(subcat)

    return Response(subcat_serializer.data)

from django.contrib import admin
from categories.models import Category, Subcategory

# Register your models here.
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']

admin.site.register(Category)
admin.site.register(Subcategory, SubcategoryAdmin)
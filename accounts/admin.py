from django.contrib import admin
from accounts.models import User, HirerProfile

# Register your models here.
class HirerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'country']


admin.site.register(User)
admin.site.register(HirerProfile, HirerProfileAdmin)
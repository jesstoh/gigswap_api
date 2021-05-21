from django.contrib import admin
from accounts.models import User, HirerProfile, TalentProfile

# Register your models here.
class HirerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'country']

class TalentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'remote', 'country']

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_hirer']

admin.site.register(User, UserAdmin)
admin.site.register(HirerProfile, HirerProfileAdmin)
admin.site.register(TalentProfile, TalentProfileAdmin)
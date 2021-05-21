from django.contrib import admin
from gigs.models import Gig

# Register your models here.
class GigAdmin(admin.ModelAdmin):
    list_display = ['poster', 'title', 'is_closed']    

admin.site.register(Gig, GigAdmin)
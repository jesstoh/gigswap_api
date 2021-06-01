from django.contrib import admin
from reviews.models import TalentReview, HirerReview

# Register your models here.
class HirerReviewAdmin(admin.ModelAdmin):
    list_display = ['hirer', 'talent', 'rating']

class TalentReviewAdmin(admin.ModelAdmin):
    list_display = ['hirer', 'talent', 'rating']

admin.site.register(TalentReview, TalentReviewAdmin)
admin.site.register(HirerReview, HirerReviewAdmin)

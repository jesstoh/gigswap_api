from django.contrib import admin
from notifications.models import Notification

# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user','title', 'is_read']

admin.site.register(Notification, NotificationAdmin)
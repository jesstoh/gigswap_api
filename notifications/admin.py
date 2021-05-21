from django.contrib import admin
from notifications.models import Notification

# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user',]

admin.site.register(Notification, NotificationAdmin)
from django.db import models
import uuid
from accounts.models import User

# Create your models here.
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, null=False)#headline of message
    message = models.TextField(null=False)
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False) #Store if notification is read by user
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
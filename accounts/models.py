from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    is_hirer = models.BooleanField(default=False)

class HirerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="hirer_profile")
    company = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.IntegerField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=20, blank=True)




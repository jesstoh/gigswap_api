from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from categories.models import Subcategory

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    is_hirer = models.BooleanField(default=False) #Determine if user is hirer or talent
    is_profile_complete = models.BooleanField(default=False) #Determine if user has completed profile

# Model for profile of hirer
class HirerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="hirer_profile")
    company = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.IntegerField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=20, blank=True)

# Storing talent profile, talent not allowed to apply job if profile is not created
class TalentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="talent_profile")
    bio = models.TextField()
    remote = models.BooleanField(default=False) #prefer remote only
    fixed_term = models.BooleanField(default=False) #prefer fixed term only
    skill = models.ManyToManyField(Subcategory, related_name="talent_profile") #Skill set category to find match gigs
    min_pay = models.IntegerField(null=False) #min hour pay
    image = models.URLField(null=False)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=20, blank=True)




from django.db import models
import uuid
from accounts.models import User
from categories.models import Subcategory

# Create your models here.
class Gig(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gig_owner')
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    subcategories = models.ManyToManyField(Subcategory, related_name='gigs')
    is_remote = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)
    hour_rate = models.IntegerField(null=True, blank=True)
    fixed_amount = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=False)
    duration_unit = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    close = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gig_winner', null=True, blank=True)
    completed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    # expired_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
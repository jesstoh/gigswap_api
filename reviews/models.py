from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from accounts.models import User
from gigs.models import Gig

# Create your models here.
#Model for reviewing talent
class TalentReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gig = models.OneToOneField(Gig,on_delete=models.CASCADE, related_name='talent_review')
    hirer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talent_reviewed_hirer')
    talent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talent_review')
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_ontime = models.BooleanField(default=True)
    quality = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    recommended = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.talent.username

#Model for reviewing hirer
class HirerReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gig = models.OneToOneField(Gig,on_delete=models.CASCADE, related_name='hirer_review')
    hirer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hirer_review') #hirer being reviewed
    talent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hirer_reviewed_talent') #talent that review hirer
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    payment_ontime = models.BooleanField(default=True)
    scope = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]) #Clarity of scope
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hirer.username

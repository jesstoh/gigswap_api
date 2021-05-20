from django.db import models
import uuid
from accounts.models import User
from gigs.models import Gig

# Create your models here.
class TalentFav(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='talent_fav')
    saved = models.ManyToManyField(Gig, related_name='talent_saved')
    applied = models.ManyToManyField(Gig, related_name='talent_applied')
    invited = models.ManyToManyField(Gig, related_name='talent_invited')

    def __str__(self):
        return self.user
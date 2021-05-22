from django.db import models
import uuid
from accounts.models import User, TalentProfile

# Create your models here.
class HirerFav(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hirer_fav')
    saved = models.ManyToManyField(TalentProfile, related_name='talent_saved')

    def __str__(self):
        return self.user.username
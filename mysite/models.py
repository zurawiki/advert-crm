from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from contracts.models import Advertiser


class UserProfile(models.Model):  
    user = models.OneToOneField(User)
    # other fields here
    advertiser =  models.OneToOneField(Advertiser, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):  
          return "%s's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)
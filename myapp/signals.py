from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import ProgrammingError

from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except ProgrammingError:
            pass
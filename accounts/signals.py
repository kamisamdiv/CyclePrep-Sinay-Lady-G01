from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile automatically whenever a new User is created.

    Superusers (made with `createsuperuser`) get the Admin role.
    Everyone else starts as a Member.
    """
    if created:
        role = Profile.Role.ADMIN if instance.is_superuser else Profile.Role.MEMBER
        Profile.objects.create(user=instance, role=role)

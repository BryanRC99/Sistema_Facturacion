from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TOTPProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_totp_profile(sender, instance, created, **kwargs):
    if created:
        TOTPProfile.objects.create(user=instance)

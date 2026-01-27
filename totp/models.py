from django.conf import settings
from django.db import models

class TOTPProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="totp_profile"
    )
    enabled = models.BooleanField(default=False)
    secret = models.CharField(max_length=64, blank=True, null=True)  # base32

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TOTP - {self.user}"

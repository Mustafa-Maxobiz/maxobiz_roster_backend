from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models.user import User


class SocialAccount(models.Model):
    class Provider(models.TextChoices):
        GOOGLE = "google", _("Google")
        APPLE = "apple", _("Apple")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    provider_user_id = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "provider_user_id")
        indexes = [
            models.Index(fields=["provider", "provider_user_id"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_user_id}"

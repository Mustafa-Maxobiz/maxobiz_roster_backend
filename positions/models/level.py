from django.db import models
from common.models import TimeStampedModel


class Level(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=20, unique=True, help_text="Short identifier, e.g., T.L for Team Lead")

    def __str__(self):
        return f"{self.name} ({self.slug})"
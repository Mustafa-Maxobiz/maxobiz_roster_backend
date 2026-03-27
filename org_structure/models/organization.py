from django.db import models
from .group import Group  # Import Group from the same models package

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organizations'
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'group'],
                name='unique_org_per_group'
            )
        ]

    def __str__(self):
        return self.name

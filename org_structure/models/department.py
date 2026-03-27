from django.db import models
from .organization import Organization
from .group import Group

class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    organizations = models.ManyToManyField(
        Organization,
        blank=True,
        related_name='departments'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments'
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
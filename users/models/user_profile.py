from django.db import models
from django.conf import settings
from positions.models.designation import Designation
from common.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    class JobStatus(models.TextChoices):
        PROBATION = "probation", "Probation"
        PERMANENT = "permanent", "Permanent"
        INTERN = "intern", "Intern"

    class WorkMode(models.TextChoices):
        ONSITE = "onsite", "Onsite"
        REMOTE = "remote", "Remote"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    pic = models.ImageField(upload_to="user_pics/", null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    job_designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles"
    )


    # shift info
    shift_start = models.TimeField(null=True, blank=True)
    shift_end = models.TimeField(null=True, blank=True)
    is_flexible = models.BooleanField(default=False)
    threshold_hours = models.DecimalField(max_digits=5, decimal_places=2, default=8.0)

    # job info
    job_status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PROBATION)
    joining_date = models.DateField(null=True, blank=True)
    hickvision_id = models.CharField(max_length=50, null=True, blank=True)
    work_mode = models.CharField(max_length=20, choices=WorkMode.choices, default=WorkMode.ONSITE)

    def __str__(self):
        return f"{self.user.username} Profile"
# users/serializers/userprofile.py
from rest_framework import serializers
from users.models.user_profile import UserProfile
from positions.models import Designation, Level

class UserProfileSerializer(serializers.ModelSerializer):
    job_designation = serializers.PrimaryKeyRelatedField(queryset=Designation.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = [
            "id", "pic", "address", "dob",
            "job_designation",
            "shift_start", "shift_end", "is_flexible", "threshold_hours",
            "job_status", "joining_date", "hickvision_id", "work_mode"
        ]
        read_only_fields = ["id"]
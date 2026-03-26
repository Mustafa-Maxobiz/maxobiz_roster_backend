from rest_framework import serializers
from users.validators import validate_username


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting an invitation and creating a user."""

    username = serializers.CharField(validators=[validate_username])
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

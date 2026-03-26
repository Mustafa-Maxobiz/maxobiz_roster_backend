# users/serializers/invitation.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from common.errors import raise_validation_error
from users.models.invites import Invitation
from users.services.invitation import is_invitation_expired

User = get_user_model()


def validate_invitation_data(email, role):
    """Validate email and role for invitation creation."""
    email = email.lower().strip() if email else None
    if not email:
        raise_validation_error("Email is required", field="email")
    if User.objects.filter(email=email).exists():
        raise_validation_error("A user with this email already exists.", field="email")

    existing_invite = Invitation.objects.filter(email__iexact=email).first()
    if existing_invite:
        # If invitation exists and is NOT expired (pending) → block with validation error
        if not is_invitation_expired(existing_invite):
            raise_validation_error(
                "A pending invitation has already been sent to this email. Please wait for it to expire or be accepted before sending a new one.",
                field="email",
            )
        # If expired, allow flow to continue (POST will create new invitation entry)

    if not role:
        raise_validation_error("Role is required", field="role")
    if role not in [choice[0] for choice in User.Role.choices]:
        raise_validation_error(
            f"Invalid role. Must be one of: {', '.join([c[0] for c in User.Role.choices])}",
            field="role",
        )
    return email, role


class InvitationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)

    def validate(self, attrs):
        attrs["email"], attrs["role"] = validate_invitation_data(
            attrs.get("email"), attrs.get("role")
        )
        return attrs
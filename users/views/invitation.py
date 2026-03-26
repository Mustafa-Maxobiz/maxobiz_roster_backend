# users/views/invitation.py
import logging
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from common.responses import APIResponse
from common.errors import raise_validation_error
from users.models.invites import Invitation
from users.serializers.invitation import InvitationSerializer
from users.services.invitation import get_or_create_invitation, send_invitation_email

User = get_user_model()
logger = logging.getLogger(__name__)


class InvitationView(generics.GenericAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        key = request.query_params.get("key")
        if key:
            try:
                invitation = Invitation.objects.get(key=key)
            except Invitation.DoesNotExist:
                return APIResponse(
                    success=False,
                    message="Invitation not found.",
                    status=status.HTTP_404_NOT_FOUND,
                )

            if invitation.key_expired():
                return APIResponse(
                    success=False,
                    message="This invitation has expired.",
                    status=status.HTTP_410_GONE,
                )

            if invitation.accepted:
                return APIResponse(
                    success=False,
                    message="This invitation has already been accepted.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return APIResponse(
                success=True,
                message="Invitation is valid.",
                data={"key": invitation.key},
                status=status.HTTP_200_OK,
            )

        if request.user.role != User.Role.ADMIN:
            raise PermissionDenied("Only administrators can list invitations.")

        accepted_param = request.query_params.get("accepted")

        invitations = Invitation.objects.filter(inviter=request.user)

        if accepted_param is not None:
            value = accepted_param.lower()
            if value in ("true", "1", "yes"):
                invitations = invitations.filter(accepted__isnull=True)
            elif value in ("false", "0", "no"):
                invitations = invitations.filter(accepted__isnull=False)
            else:
                raise_validation_error(
                    "accepted must be 'true' or 'false'", field="accepted"
                )

        invitations = invitations.order_by("-id")

        data = [
            {
                "email": inv.email,
                "role": inv.role,
                "accepted": bool(inv.accepted) if getattr(inv, "accepted", None) else False,
                "sent": inv.sent,
            }
            for inv in invitations
        ]

        return APIResponse(
            success=True,
            message="Invitations fetched successfully.",
            data=data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        if request.user.role != User.Role.ADMIN:
            raise PermissionDenied("Only administrators can send invitations.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]

        invitation, created = get_or_create_invitation(
            email=email, role=role, inviter=request.user
        )

        try:
            send_invitation_email(invitation, request)
        except Exception:
            logger.exception(f"Failed to send invitation email to {email}")
            return APIResponse(
                success=False,
                message="Invitation created but email could not be sent. Please try again.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        message = "Invitation sent successfully." if created else "Invitation resent successfully."

        return APIResponse(
            success=True,
            message=message,
            data={"email": invitation.email, "role": invitation.role},
            status=status_code,
        )
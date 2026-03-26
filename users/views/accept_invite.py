from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from common.responses import APIResponse
from common.errors import raise_validation_error
from users.serializers.accept_invite import AcceptInvitationSerializer
from users.services.user_services import UserServices
from users.services.otp_service import OTPService


class AcceptInvitationView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AcceptInvitationSerializer

    def post(self, request, *args, **kwargs):
        key = request.data.get("key")
        if not key:
            raise_validation_error("Invitation key is required", field="key")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserServices.create_user_with_invitation(key, **serializer.validated_data)

        success, message = OTPService.send_otp(user.email, user=user)
        if not success:
            raise_validation_error(message, field="otp")

        return APIResponse(
            success=True,
            message="OTP sent to your email. Please verify to complete account activation.",
            data={"email": user.email, "otp_required": True, "validity_minutes": 5},
            status=status.HTTP_201_CREATED
        )

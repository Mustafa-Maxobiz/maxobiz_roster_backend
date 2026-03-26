from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from common.errors import raise_validation_error
from common.responses import APIResponse
from users.services.forget_password import ForgetPasswordService


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            raise_validation_error("Email is required", field="email")

        ForgetPasswordService.request_password_reset(email)
        return APIResponse(
            success=True,
            message="If an account exists, a reset link has been sent.",
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")

        errors = {}
        if not uid:
            errors["uid"] = "UID is required"
        if not token:
            errors["token"] = "Token is required"
        if not new_password:
            errors["password"] = "Password is required"
        if errors:
            raise_validation_error(errors)

        success, message = ForgetPasswordService.reset_password(uid, token, new_password)
        if not success:
            raise_validation_error(message, field="detail")

        return APIResponse(
            success=True,
            message=message,
            status=status.HTTP_200_OK,
        )

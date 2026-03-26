from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from common.responses import APIResponse
from common.errors import raise_validation_error
from users.serializers.auth import LoginSerializer
from users.serializers.user import UserDetailSerializer
from users.services.brute_force_service import (
    maybe_delay_login,
    record_login_failure,
    clear_login_failures,
)
from users.services.otp_service import OTPService

User = get_user_model()


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']

        maybe_delay_login(request, email)
        try:
            user = authenticate(request, username=email, password=password)
        except DjangoPermissionDenied:
            raise PermissionDenied("Too many failed login attempts. Try again later.")

        if not user:
            record_login_failure(request, email)
            raise AuthenticationFailed("Invalid credentials")

        clear_login_failures(request, email)

        # OTP required
        # if user.is_otp_required:
        if not user.is_email_verified or user.is_otp_required:
            success, message = OTPService.send_otp(email, user=user)
            if not success:
                raise_validation_error(message, field="otp")
            return APIResponse(
                success=True,
                message="OTP sent to your email. Please verify to complete login.",
                data={"email": email, "otp_required": True, "validity_minutes": 5},
                status=status.HTTP_200_OK
            )

        # Generate tokens if OTP not required
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user_serializer = UserDetailSerializer(user, context={'request': request})
        data = user_serializer.data.copy()
        data.update({
            "access_token": str(access),
            "refresh_token": str(refresh),
            "otp_required": False
        })

        user.last_login = now()
        user.save(update_fields=["last_login"])

        return APIResponse(
            success=True,
            message="Login successful",
            data=data,
            status=status.HTTP_200_OK
        )


class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            raise_validation_error({"email": "Email is required", "otp": "OTP is required"})

        if len(otp) != 6 or not otp.isdigit():
            raise_validation_error("OTP must be a 6-digit number", field="otp")

        success, message = OTPService.verify_otp(email, otp)
        if not success:
            raise_validation_error(message, field="otp")

        # Issue tokens
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            raise NotFound("User not found")

        if not user.is_active:
            user.is_active = True
            user.is_email_verified = True
            user.save(update_fields=["is_active", "is_email_verified"])

        user.last_login = now()
        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user_serializer = UserDetailSerializer(user, context={'request': request})
        data = user_serializer.data.copy()
        data.update({
            "access_token": str(access),
            "refresh_token": str(refresh)
        })

        return APIResponse(
            success=True,
            message="Login successful",
            data=data,
            status=200
        )


class ResendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            raise_validation_error("Email is required", field="email")

        try:
            User.objects.get(email=email.lower())
        except User.DoesNotExist:
            raise NotFound("User not found")

        success, message = OTPService.resend_otp(email)
        if not success:
            raise_validation_error(message, field="otp")

        return APIResponse(
            success=True,
            message="OTP resent successfully to your email",
            data={"validity_minutes": 5},
            status=status.HTTP_200_OK
        )

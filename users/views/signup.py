from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from common.responses import APIResponse
from common.errors import raise_validation_error
from users.serializers.signup import UserSignupSerializer
from users.services.user_services import UserServices

User = get_user_model()


class SignupView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignupSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        key = request.data.get("key")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if key:
            user = UserServices.create_user_with_invitation(key, **serializer.validated_data)
        else:
            user = UserServices.create_user(is_active=False, **serializer.validated_data)

        success, message = UserServices.send_signup_otp(user)
        if not success:
            raise_validation_error(message, field="otp")

        return APIResponse(
            success=True,
            message="OTP sent to your email. Please verify to complete signup.",
            data={"email": user.email, "otp_required": True, "validity_minutes": 5},
            status=status.HTTP_201_CREATED
        )

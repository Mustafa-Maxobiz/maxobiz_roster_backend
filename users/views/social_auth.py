from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from common.errors import raise_validation_error
from common.responses import APIResponse
from users.serializers.user import UserDetailSerializer
from users.services.social_auth_service import (
    verify_social_token,
    get_or_create_user_from_social,
)


class SocialLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        provider = (request.data.get("provider") or "").lower()
        id_token = request.data.get("id_token")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        errors = {}
        if not provider:
            errors["provider"] = "Provider is required"
        if not id_token:
            errors["id_token"] = "id_token is required"
        if errors:
            raise_validation_error(errors)

        payload = verify_social_token(provider, id_token)
        user, _created = get_or_create_user_from_social(payload, first_name, last_name)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user_serializer = UserDetailSerializer(user, context={"request": request})
        data = user_serializer.data.copy()
        data.update({
            "access_token": str(access),
            "refresh_token": str(refresh),
            "otp_required": False,
        })

        return APIResponse(
            success=True,
            message="Login successful",
            data=data,
            status=status.HTTP_200_OK,
        )

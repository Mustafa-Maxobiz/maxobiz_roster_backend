from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from common.responses import APIResponse
from common.errors import raise_validation_error

User = get_user_model()

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            raise_validation_error("Refresh token is required", field="refresh_token")

        try:
            user = request.user
            user.last_logout = now()
            user.save(update_fields=["last_logout"])
            token = RefreshToken(refresh_token)
            token.blacklist()
            return APIResponse(
                success=True,
                message="Successfully logged out",
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            raise_validation_error("Invalid or expired token", field="refresh_token")

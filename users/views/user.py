from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from common.responses import APIResponse
from common.errors import raise_validation_error
from common.permissions import AdminOnlyPermission
from users.serializers.user import UserDetailSerializer
from users.services.user_services import UserServices

User = get_user_model()


class UserView(generics.GenericAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    permissions_per_action = {
        "GET": [IsAuthenticated],
        "PATCH": [IsAuthenticated],
        "DELETE": [AdminOnlyPermission],
    }

    def get_permissions(self):
        permission_classes = self.permissions_per_action.get(self.request.method)
        if permission_classes is None:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get(self, request, *args, **kwargs):
        role_type = request.query_params.get("role_type")

        # ✅ Case 1: No query param → return current logged-in user
        if not role_type:
            serializer = self.get_serializer(request.user)
            return APIResponse(
                success=True,
                message="User details fetched successfully",
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        # ✅ Case 2: role_type passed → only ADMIN can access
        if request.user.role != User.Role.ADMIN:
            raise PermissionDenied("Only admin can filter users by role")

        # Validate role_type
        valid_roles = [choice[0] for choice in User.Role.choices]
        if role_type not in valid_roles:
            raise_validation_error("Invalid role type", field="role_type")

        users = UserServices.get_users_by_role(role_type)
        serializer = self.get_serializer(users, many=True)

        return APIResponse(
            success=True,
            message=f"Users with role '{role_type}' fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        try:
            user = UserServices.update_user(request.user, request.data)
        except Exception as e:
            raise_validation_error(getattr(e, "detail", str(e)))

        # None means OTP was just sent, not a full update
        if user is None:
            return APIResponse(
                success=True,
                message="OTP sent to your new email for verification",
                status=status.HTTP_200_OK
            )

        serializer = UserDetailSerializer(user, context={"request": request})
        return APIResponse(
            success=True,
            message="Profile updated successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, user_id=None):
        if not user_id:
            raise_validation_error("User id is required", field="user_id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")

        if user.is_deleted:
            return APIResponse(
                success=True,
                message="User already deleted",
                status=status.HTTP_200_OK
            )

        user.is_active = False
        user.is_deleted = True
        user.save(update_fields=["is_active", "is_deleted"])
        return APIResponse(
            success=True,
            message="User deleted successfully",
            status=status.HTTP_200_OK
        )

# users/views/userprofile.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from common.responses import APIResponse
from users.models.user_profile import UserProfile
from users.serializers.user_profile import UserProfileSerializer

class UserProfileView(generics.GenericAPIView):
    """
    GET  -> fetch current user's profile
    POST -> create or update current user's profile
    """
    serializer_class = UserProfileSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Use select_related for OneToOne and ForeignKey fields
        to avoid extra queries when accessing nested objects.
        """
        profile, created = UserProfile.objects.select_related(
            'job_designation', 'user'
        ).get_or_create(user=self.request.user)
        return profile

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return APIResponse(
            success=True,
            message="User profile fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        """
        Combined create/update:
        - If profile exists → update with partial=True
        - If profile doesn't exist → create
        """
        profile = self.get_object()  # get or create
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # attach user explicitly
        return APIResponse(
            success=True,
            message="User profile saved successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )
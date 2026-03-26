from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.services.user_services import UserServices

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for response"""
    role_label = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'role', 'role_label', 'is_email_verified', 'is_active',
                  'last_logout', 'date_joined']
        read_only_fields = ['id', 'last_logout', 'date_joined']

    def create(self, validated_data):
        """Use service to create user"""
        return UserServices.create_user(**validated_data)

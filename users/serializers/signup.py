from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.validators import validate_email, validate_username

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    """Serializer for user signup"""

    email = serializers.EmailField(validators=[validate_email])
    username = serializers.CharField(validators=[validate_username])
    password = serializers.CharField(write_only=True, min_length=8)


    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']

    def validate_email(self, value):
        return value.lower()

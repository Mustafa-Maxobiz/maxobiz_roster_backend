from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

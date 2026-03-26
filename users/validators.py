from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


def validate_email(email):
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError(
            "User with this email address already exists."
        )


def validate_username(username):
    if User.objects.filter(username=username).exists():
        raise serializers.ValidationError(
            "A user with that username already exists."
        )

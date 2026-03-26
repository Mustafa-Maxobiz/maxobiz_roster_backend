import secrets

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from jwt.algorithms import RSAAlgorithm
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from users.models.social_account import SocialAccount

User = get_user_model()

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"


def _generate_unique_username(email):
    base = (email.split("@")[0] if email else "user").lower()
    candidate = base
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{secrets.randbelow(10000)}"
    return candidate


def _verify_google_id_token(id_token):
    if not settings.GOOGLE_CLIENT_ID:
        raise ValidationError({"detail": "GOOGLE_CLIENT_ID is not configured"})

    response = requests.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token}, timeout=10)
    if response.status_code != 200:
        raise AuthenticationFailed("Invalid Google token")

    data = response.json()
    if data.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise AuthenticationFailed("Google token audience mismatch")

    email = data.get("email")
    email_verified = data.get("email_verified") == "true" or data.get("email_verified") is True
    sub = data.get("sub")
    given_name = data.get("given_name")
    family_name = data.get("family_name")

    if not email or not sub:
        raise AuthenticationFailed("Google token missing required claims")

    return {
        "provider": "google",
        "provider_user_id": sub,
        "email": email.lower(),
        "email_verified": email_verified,
        "first_name": given_name or "",
        "last_name": family_name or "",
    }


def _get_apple_public_key(kid, jwks):
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return RSAAlgorithm.from_jwk(key)
    return None


def _verify_apple_id_token(id_token):
    if not settings.APPLE_CLIENT_ID:
        raise ValidationError({"detail": "APPLE_CLIENT_ID is not configured"})

    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get("kid")
    if not kid:
        raise AuthenticationFailed("Invalid Apple token header")

    jwks_response = requests.get(APPLE_JWKS_URL, timeout=10)
    if jwks_response.status_code != 200:
        raise AuthenticationFailed("Unable to fetch Apple public keys")

    public_key = _get_apple_public_key(kid, jwks_response.json())
    if not public_key:
        raise AuthenticationFailed("Apple public key not found")

    try:
        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID,
            issuer=settings.APPLE_ISSUER,
        )
    except jwt.PyJWTError:
        raise AuthenticationFailed("Invalid Apple token")

    email = payload.get("email")
    sub = payload.get("sub")

    if not sub:
        raise AuthenticationFailed("Apple token missing required claims")

    return {
        "provider": "apple",
        "provider_user_id": sub,
        "email": (email or "").lower(),
        "email_verified": True,
        "first_name": "",
        "last_name": "",
    }


def verify_social_token(provider, id_token):
    if provider == "google":
        return _verify_google_id_token(id_token)
    if provider == "apple":
        return _verify_apple_id_token(id_token)
    raise ValidationError({"provider": "Unsupported provider"})


def get_or_create_user_from_social(payload, first_name=None, last_name=None):
    provider = payload["provider"]
    provider_user_id = payload["provider_user_id"]
    email = payload.get("email")

    social_account = SocialAccount.objects.filter(
        provider=provider,
        provider_user_id=provider_user_id,
    ).select_related("user").first()

    if social_account:
        user = social_account.user
        if user.is_deleted:
            raise AuthenticationFailed("Account is deleted")
        social_account.last_login_at = timezone.now()
        social_account.save(update_fields=["last_login_at"])
        return user, False

    user = None
    if email:
        user = User.objects.filter(email=email.lower()).first()

    if user and user.is_deleted:
        raise AuthenticationFailed("Account is deleted")

    created = False
    if not user:
        if not email:
            raise AuthenticationFailed("Email is required for account creation")
        username = _generate_unique_username(email)
        user = User.objects.create_customer(
            email=email,
            username=username,
            first_name=first_name or payload.get("first_name", ""),
            last_name=last_name or payload.get("last_name", ""),
            role=User.Role.CUSTOMER,
            is_active=True,
        )
        created = True

    if payload.get("email_verified"):
        user.is_email_verified = True
    user.is_otp_required = False
    user.save(update_fields=["is_email_verified", "is_otp_required"])

    SocialAccount.objects.create(
        user=user,
        provider=provider,
        provider_user_id=provider_user_id,
        email=email or None,
    )
    return user, created

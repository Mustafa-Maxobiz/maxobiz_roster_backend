from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class ForgetPasswordService:
    @staticmethod
    def _build_reset_link(uidb64, token):
        base_url = settings.FRONTEND_URL.rstrip("/")
        query = urlencode({"uid": uidb64, "token": token})
        return f"{base_url}/reset-password?{query}"

    @staticmethod
    def request_password_reset(email):
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return True, None

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = ForgetPasswordService._build_reset_link(uidb64, token)

        timeout_hours = int(getattr(settings, "PASSWORD_RESET_TIMEOUT", 0) // 3600)
        subject = "Reset your password"
        message = (
            "You requested a password reset.\n\n"
            f"Reset link: {reset_link}\n\n"
            f"This link expires in {timeout_hours} hours."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True, reset_link

    @staticmethod
    def reset_password(uidb64, token, new_password):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return False, "Invalid reset link"

        if not token_generator.check_token(user, token):
            return False, "Invalid or expired reset link"

        try:
            validate_password(new_password, user=user)
        except ValidationError as exc:
            raise ValidationError({"password": list(exc.messages)})

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return True, "Password reset successfully"

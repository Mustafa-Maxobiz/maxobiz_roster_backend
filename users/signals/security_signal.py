import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.dispatch import receiver
from rest_framework.exceptions import PermissionDenied

from axes.signals import user_locked_out
from users.tasks.security_task import send_lockout_notification_task

logger = logging.getLogger(__name__)
User = get_user_model()


def _extract_login_email(request, username, credentials):
    if username:
        return username
    if credentials:
        return credentials.get("email") or credentials.get("username")
    if request is not None:
        data = getattr(request, "data", None) or {}
        return data.get("email") or data.get("username")
    return None


@receiver(user_locked_out)
def handle_user_locked_out(sender, request=None, username=None, credentials=None, **kwargs):
    email = _extract_login_email(request, username, credentials)
    if email:
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            user = None

        if user:
            cache_key = f"lockout_notify:{user.pk}"
            window = settings.BRUTE_FORCE_LOCKOUT_NOTIFY_WINDOW_SECONDS
            threshold = settings.BRUTE_FORCE_LOCKOUT_NOTIFY_THRESHOLD

            count = cache.get(cache_key, 0) + 1
            cache.set(cache_key, count, window)

            if count >= threshold:
                try:
                    send_lockout_notification_task.delay(user.email)
                except Exception as exc:
                    logger.error("Failed to queue lockout notification: %s", str(exc))
                cache.delete(cache_key)

    raise PermissionDenied("Too many failed login attempts. Try again later.")

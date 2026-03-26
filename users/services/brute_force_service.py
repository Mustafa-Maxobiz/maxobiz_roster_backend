import random
import time

from django.conf import settings
from django.core.cache import cache


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _get_fail_cache_key(email, ip_address):
    return f"login_failures:{email}:{ip_address}"


def maybe_delay_login(request, email):
    threshold = settings.BRUTE_FORCE_DELAY_THRESHOLD
    if threshold <= 0:
        return

    ip_address = _get_client_ip(request)
    cache_key = _get_fail_cache_key(email, ip_address)
    attempts = cache.get(cache_key, 0)

    if attempts >= threshold:
        min_delay = settings.BRUTE_FORCE_DELAY_MIN_SECONDS
        max_delay = settings.BRUTE_FORCE_DELAY_MAX_SECONDS
        if max_delay < min_delay:
            max_delay = min_delay
        time.sleep(random.uniform(min_delay, max_delay))


def record_login_failure(request, email):
    ip_address = _get_client_ip(request)
    cache_key = _get_fail_cache_key(email, ip_address)
    window = settings.BRUTE_FORCE_DELAY_WINDOW_SECONDS
    attempts = cache.get(cache_key, 0) + 1
    cache.set(cache_key, attempts, window)


def clear_login_failures(request, email):
    ip_address = _get_client_ip(request)
    cache_key = _get_fail_cache_key(email, ip_address)
    cache.delete(cache_key)

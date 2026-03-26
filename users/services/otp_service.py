import logging
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache

from users.tasks.otp_task import send_otp_email_task

User = get_user_model()
logger = logging.getLogger(__name__)

class OTPService:
    OTP_COOLDOWN_SECONDS = 60
    OTP_MAX_ATTEMPTS_PER_HOUR = 5

    @staticmethod
    def send_otp(email, purpose=None, user=None):
        email = email.lower()
        can_send, wait_time = OTPService._check_rate_limit(email, purpose)
        if not can_send:
            return False, f"Please wait {wait_time} seconds before requesting a new OTP"

        try:
            if user is None:
                user = User.objects.get(email=email)
            otp_code = user.generate_otp()
        except User.DoesNotExist:
            return False, "User not found"

        try:
            send_otp_email_task.delay(email, otp_code)
        except Exception as e:
            logger.error(f"Failed to queue OTP email for {email}: {str(e)}")
            return False, "Failed to send OTP. Please try again."

        OTPService._record_otp_request(email, purpose)
        return True, "OTP sent successfully to your email"

    @staticmethod
    def verify_otp(email, otp_code, purpose=None, user=None):
        email = email.lower()
        try:
            if user is None:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            return False, "User not found"

        is_valid = user.verify_otp(otp_code)

        if is_valid:
            OTPService._clear_rate_limit(email, purpose)
            was_unverified = not user.is_email_verified
            if was_unverified:
                user.is_email_verified = True
                if user.is_otp_required:
                    user.is_otp_required = False
                user.save(update_fields=['is_email_verified', 'is_otp_required'])
            return True, "OTP verified successfully"
        else:
            return False, "Invalid or expired OTP"

    @staticmethod
    def resend_otp(email, purpose=None):
        return OTPService.send_otp(email, purpose=purpose)

    # Rate Limiting Helpers
    @staticmethod
    def _get_cooldown_key(email, purpose):
        suffix = purpose or "default"
        return f"otp_cooldown:{suffix}:{email}"

    @staticmethod
    def _get_attempts_key(email, purpose):
        suffix = purpose or "default"
        return f"otp_attempts:{suffix}:{email}"

    @staticmethod
    def _check_rate_limit(email, purpose):
        cooldown_key = OTPService._get_cooldown_key(email, purpose)
        attempts_key = OTPService._get_attempts_key(email, purpose)

        now = int(time.time())
        cooldown_until = cache.get(cooldown_key)
        if cooldown_until and cooldown_until > now:
            return False, cooldown_until - now

        attempts_data = cache.get(attempts_key)
        if attempts_data:
            attempts_count, window_start = attempts_data
            if now - window_start >= 3600:
                attempts_count = 0
                window_start = now
        else:
            attempts_count = 0
            window_start = now

        if attempts_count >= OTPService.OTP_MAX_ATTEMPTS_PER_HOUR:
            return False, max(0, 3600 - (now - window_start))

        return True, 0

    @staticmethod
    def _record_otp_request(email, purpose):
        cooldown_key = OTPService._get_cooldown_key(email, purpose)
        attempts_key = OTPService._get_attempts_key(email, purpose)

        now = int(time.time())
        cache.set(cooldown_key, now + OTPService.OTP_COOLDOWN_SECONDS, OTPService.OTP_COOLDOWN_SECONDS)

        attempts_data = cache.get(attempts_key)
        if attempts_data:
            attempts_count, window_start = attempts_data
            if now - window_start >= 3600:
                attempts_count = 0
                window_start = now
        else:
            attempts_count = 0
            window_start = now

        cache.set(attempts_key, (attempts_count + 1, window_start), 3600)

    @staticmethod
    def _clear_rate_limit(email, purpose):
        cache.delete(OTPService._get_cooldown_key(email, purpose))
        cache.delete(OTPService._get_attempts_key(email, purpose))

# from django.utils import timezone
#
# class AuthService:
#     """Service layer for login attempts"""
#
#     @staticmethod
#     def handle_failed_login(user):
#         user.failed_login_attempts += 1
#         if user.failed_login_attempts >= 5:
#             user.login_ban_until = timezone.now() + timezone.timedelta(hours=6)
#             user.failed_login_attempts = 0
#             user.save()
#             return True, "Too many failed login attempts. Account locked for 6 hours."
#         user.save()
#         attempts_left = 5 - user.failed_login_attempts
#         return False, f"Invalid credentials. {attempts_left} attempts remaining."
#
#     @staticmethod
#     def reset_login_attempts(user):
#         if user.failed_login_attempts > 0:
#             user.failed_login_attempts = 0
#             user.save()

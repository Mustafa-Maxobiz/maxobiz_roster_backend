import pyotp
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.managers.managers import UserManager  # <- now works

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        EXPERT = "expert", _("Expert")
        CUSTOMER = "customer", _("Customer")

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    # failed_login_attempts = models.PositiveIntegerField(default=0)
    # login_ban_until = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # OTP fields
    otp_secret = models.CharField(max_length=32, blank=True, null=True, help_text="Secret key for TOTP generation")
    is_otp_required = models.BooleanField(
        default=True,
        help_text="Whether OTP is required for login (2FA setting)"
    )
    last_logout = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()  # attach custom manager

    class Meta:
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_email_verified"]),
            models.Index(fields=["is_otp_required"]),
            models.Index(fields=["is_deleted"]),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()

        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()

        super().save(*args, **kwargs)

    def mark_logged_out(self):
        self.last_logout = timezone.now()
        self.save(update_fields=["last_logout"])

    def generate_otp(self):
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()
            self.save(update_fields=['otp_secret'])
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        return totp.now()

    def verify_otp(self, otp_code):
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        return totp.verify(otp_code, valid_window=1)

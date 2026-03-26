# users/models/invites.py
from django.db import models
from invitations.base_invitation import AbstractBaseInvitation
from users.models import User


class Invitation(AbstractBaseInvitation):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=User.Role.choices,
        default=User.Role.EMP,
    )
    inviter = models.ForeignKey(
        User,
        related_name="sent_invitations",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        from users.services.invitation import generate_invitation_key
        key = generate_invitation_key()
        return cls._default_manager.create(email=email, key=key, inviter=inviter, **kwargs)

    def key_expired(self):
        from users.services.invitation import is_invitation_expired
        return is_invitation_expired(self)

    def send_invitation(self, request, **kwargs):
        from users.services.invitation import send_invitation_email
        send_invitation_email(self, request)

    def __str__(self):
        return f"Invitation<{self.email} | role={self.role}>"

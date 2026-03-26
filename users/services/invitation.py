# users/services/invitation.py
import datetime
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.urls import reverse
from invitations.app_settings import app_settings
from invitations.adapters import get_invitations_adapter
from users.models.invites import Invitation


def generate_invitation_key():
    return get_random_string(64).lower()


def is_invitation_expired(invitation):
    if not invitation.sent:
        return False
    expiration_date = invitation.sent + datetime.timedelta(days=app_settings.INVITATION_EXPIRY)
    return expiration_date <= timezone.now()


def get_or_create_invitation(email, role, inviter):
    existing = Invitation.objects.filter(email__iexact=email).first()
    if existing:
        # If expired, create a NEW invitation entry (don't update existing)
        # Note: Pending invitations are already blocked by serializer validation
        invitation = Invitation.create(email=email, inviter=inviter, role=role)
        return invitation, True
    
    invitation = Invitation.create(email=email, inviter=inviter, role=role)
    return invitation, True


def send_invitation_email(invitation, request):
    # Use frontend URL for the invitation link (customize the path as needed)
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    # Use a simpler frontend path - customize this to match your frontend route
    invite_url = f"{frontend_url.rstrip('/')}/invite/{invitation.key}/"
    
    # Get site name from settings or use default
    site_name = getattr(settings, 'SITE_NAME', 'MaxobizRoster')
    
    ctx = {
        "invite_url": invite_url,
        "email": invitation.email,
        "inviter": invitation.inviter,
        "site_name": site_name,  # Required by django-invitations adapter
    }
    get_invitations_adapter().send_mail(
        "invitations/email/email_invite", invitation.email, ctx
    )
    invitation.sent = timezone.now()
    invitation.save(update_fields=["sent"])

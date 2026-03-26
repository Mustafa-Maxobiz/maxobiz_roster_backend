import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_lockout_notification_task(self, email):
    try:
        subject = "Account temporarily locked"
        html_message = """
        <html>
        <body>
            <h2>Account Temporarily Locked</h2>
            <p>
                We detected repeated failed login attempts and temporarily locked your account
                for your security. If this wasn't you, please reset your password.
            </p>
            <p>
                If you need help, please contact support.
            </p>
        </body>
        </html>
        """
        plain_message = strip_tags(html_message)
        email_msg = EmailMultiAlternatives(
            subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email]
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)
        logger.info("Lockout notification sent to %s", email)
        return {"status": "success", "email": email}
    except Exception as exc:
        logger.error("Failed to send lockout notification to %s: %s", email, str(exc))
        raise self.retry(exc=exc, countdown=60)

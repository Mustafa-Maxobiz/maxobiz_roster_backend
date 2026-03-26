from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_otp_email_task(self, email, otp_code):
    try:
        subject = "Your OTP Code"
        html_message = f"""
        <html>
        <body>
            <h2>Your OTP Code</h2>
            <p>Hello,</p>
            <div style="font-size:32px;font-weight:bold">{otp_code}</div>
            <p>This OTP is valid for <strong>5 minutes</strong>.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        plain_message = strip_tags(html_message)
        email_msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)
        logger.info(f"OTP email sent to {email}")
        return {"status": "success", "email": email}
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        raise self.retry(exc=e, countdown=60)

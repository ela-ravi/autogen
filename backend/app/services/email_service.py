import logging

import resend

from app.config import settings

logger = logging.getLogger(__name__)


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """Send a 6-digit OTP verification code via Resend."""
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set — skipping OTP email to %s (code: %s)", to_email, otp_code)
        return True

    resend.api_key = settings.RESEND_API_KEY

    try:
        resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": f"Your verification code: {otp_code}",
            "html": (
                f"<div style='font-family:sans-serif;max-width:400px;margin:0 auto;padding:24px'>"
                f"<h2 style='margin-bottom:8px'>Verify your email</h2>"
                f"<p style='color:#555;margin-bottom:24px'>Enter this code to complete your sign-up:</p>"
                f"<div style='font-size:36px;font-weight:bold;letter-spacing:8px;text-align:center;"
                f"background:#f4f4f5;border-radius:8px;padding:16px;margin-bottom:24px'>{otp_code}</div>"
                f"<p style='color:#888;font-size:13px'>This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.</p>"
                f"<p style='color:#888;font-size:13px'>If you didn't create an account, you can ignore this email.</p>"
                f"</div>"
            ),
        })
        return True
    except Exception:
        logger.exception("Failed to send OTP email to %s", to_email)
        return False

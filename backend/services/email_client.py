"""Email notification service for wholesale inquiries.

Falls back gracefully if SMTP is not configured.
"""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings

logger = logging.getLogger(__name__)

RECIPIENT = "info@s-natural.xyz"


def _is_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_password)


async def send_inquiry_notification(inquiry) -> bool:
    """Send an email notification for a new wholesale inquiry."""
    if not _is_configured():
        logger.info("SMTP not configured — skipping email notification")
        return False

    try:
        import aiosmtplib
    except ImportError:
        logger.warning("aiosmtplib not installed — skipping email notification")
        return False

    subject = f"New Wholesale Inquiry from {inquiry.company}"

    html_body = f"""\
<div style="font-family:'Work Sans',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <div style="background:#406546;padding:24px 32px;border-radius:16px 16px 0 0;text-align:center">
    <h2 style="color:#fff;margin:0;font-size:18px;font-weight:600">New Wholesale Inquiry</h2>
  </div>
  <div style="background:#fff;padding:32px;border:1px solid #e8e8e8;border-top:none;border-radius:0 0 16px 16px">
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <tr><td style="padding:10px 12px;color:#7a766d;width:140px;vertical-align:top">Company</td>
          <td style="padding:10px 12px;font-weight:500">{inquiry.company}</td></tr>
      <tr style="background:#fafaf8"><td style="padding:10px 12px;color:#7a766d">Contact</td>
          <td style="padding:10px 12px;font-weight:500">{inquiry.name}</td></tr>
      <tr><td style="padding:10px 12px;color:#7a766d">Email</td>
          <td style="padding:10px 12px"><a href="mailto:{inquiry.email}" style="color:#406546">{inquiry.email}</a></td></tr>
      <tr style="background:#fafaf8"><td style="padding:10px 12px;color:#7a766d">Phone</td>
          <td style="padding:10px 12px">{inquiry.phone or '—'}</td></tr>
      <tr><td style="padding:10px 12px;color:#7a766d">Country</td>
          <td style="padding:10px 12px">{inquiry.country or '—'}</td></tr>
      <tr style="background:#fafaf8"><td style="padding:10px 12px;color:#7a766d">Quantity</td>
          <td style="padding:10px 12px;font-weight:600;color:#406546">{inquiry.quantity} kg</td></tr>
      <tr><td style="padding:10px 12px;color:#7a766d">Business Type</td>
          <td style="padding:10px 12px">{inquiry.use_case or '—'}</td></tr>
    </table>
    {"<div style='margin-top:20px;padding:16px;background:#f9f0e2;border-radius:12px'><p style='margin:0 0 4px;font-size:12px;color:#7a766d'>Message</p><p style='margin:0;font-size:14px;line-height:1.6'>" + inquiry.message + "</p></div>" if inquiry.message else ""}
    <p style="margin-top:24px;font-size:12px;color:#bbb;text-align:center">
      Sent via NAKAI Wholesale Inquiry Form
    </p>
  </div>
</div>"""

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_user
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg["Reply-To"] = inquiry.email
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=settings.smtp_port == 465,
            start_tls=settings.smtp_port == 587,
        )
        logger.info(f"Inquiry notification sent for {inquiry.company}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

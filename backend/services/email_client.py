"""Email notification service for wholesale inquiries.

Falls back gracefully if SMTP is not configured.
"""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings

logger = logging.getLogger(__name__)

RECIPIENT = "wholesale@nakaiinfo.com"


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
    msg["From"] = f"NAKAI Wholesale <{RECIPIENT}>"
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


async def send_contact_inquiry_notification(inquiry) -> bool:
    """Send an email notification for a new contact page inquiry."""
    if not _is_configured():
        logger.info("SMTP not configured — skipping contact email notification")
        return False

    try:
        import aiosmtplib
    except ImportError:
        logger.warning("aiosmtplib not installed — skipping contact email notification")
        return False

    type_label = getattr(inquiry, 'inquiry_type', 'General')
    subject = f"New {type_label} Inquiry from {getattr(inquiry, 'name', 'Website')}"

    # Build details rows
    rows = []
    if getattr(inquiry, 'name', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px;width:120px">Name</td><td style="padding:8px 16px;font-size:14px">{inquiry.name}</td></tr>')
    if getattr(inquiry, 'email', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Email</td><td style="padding:8px 16px;font-size:14px"><a href="mailto:{inquiry.email}">{inquiry.email}</a></td></tr>')
    if getattr(inquiry, 'company', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Company</td><td style="padding:8px 16px;font-size:14px">{inquiry.company}</td></tr>')
    if getattr(inquiry, 'phone', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Phone</td><td style="padding:8px 16px;font-size:14px">{inquiry.phone}</td></tr>')
    if getattr(inquiry, 'business_type', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Business Type</td><td style="padding:8px 16px;font-size:14px">{inquiry.business_type}</td></tr>')
    if getattr(inquiry, 'monthly_volume', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Monthly Volume</td><td style="padding:8px 16px;font-size:14px">{inquiry.monthly_volume}</td></tr>')
    dates = getattr(inquiry, 'preferred_dates', None)
    if dates:
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Preferred Dates</td><td style="padding:8px 16px;font-size:14px">{", ".join(dates)}</td></tr>')
    if getattr(inquiry, 'message', ''):
        rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px;vertical-align:top">Message</td><td style="padding:8px 16px;font-size:14px;white-space:pre-wrap">{inquiry.message}</td></tr>')

    rows_html = ''.join(rows)
    html_body = (
        '<div style="font-family:\'Work Sans\',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">'
        '<div style="background:#406546;padding:24px 32px;border-radius:16px 16px 0 0;text-align:center">'
        f'<h2 style="color:#fff;margin:0;font-size:18px;font-weight:600">New {type_label} Inquiry</h2>'
        '</div>'
        '<div style="background:#fff;padding:32px;border:1px solid #e8e8e8;border-top:none;border-radius:0 0 16px 16px">'
        f'<table style="width:100%;border-collapse:collapse;font-size:14px">{rows_html}</table>'
        '</div>'
        '</div>'
    )

    # Determine recipient based on inquiry type
    to_email = "wholesale@nakaiinfo.com" if type_label == "Wholesale" else "contact@nakaiinfo.com"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
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
        logger.info(f"Contact inquiry notification sent to {to_email}")
        return True
    except Exception as e:
        logger.warning(f"Failed to send contact inquiry email: {e}")
        return False

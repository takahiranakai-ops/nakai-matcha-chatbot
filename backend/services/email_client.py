"""Email notification service for wholesale inquiries.

Uses Resend API for reliable delivery.
"""
import html
import logging

logger = logging.getLogger(__name__)

RECIPIENT = "wholesale@nakaiinfo.com"


async def send_inquiry_notification(inquiry) -> bool:
    """Send email notification to team via Resend API."""
    try:
        from services.resend_client import send_email

        html_body = f"""\
<div style="font-family:'Work Sans',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <div style="background:#406546;padding:24px 32px;border-radius:16px 16px 0 0;text-align:center">
    <h2 style="color:#fff;margin:0;font-size:18px;font-weight:600">New Wholesale Inquiry</h2>
  </div>
  <div style="background:#fff;padding:32px;border:1px solid #e8e8e8;border-top:none;border-radius:0 0 16px 16px">
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <tr><td style="padding:10px 12px;color:#7a766d;width:140px;vertical-align:top">Company</td>
          <td style="padding:10px 12px;font-weight:500">{html.escape(inquiry.company or '')}</td></tr>
      <tr style="background:#fafaf8"><td style="padding:10px 12px;color:#7a766d">Contact</td>
          <td style="padding:10px 12px;font-weight:500">{html.escape(inquiry.name or '')}</td></tr>
      <tr><td style="padding:10px 12px;color:#7a766d">Email</td>
          <td style="padding:10px 12px"><a href="mailto:{html.escape(inquiry.email or '')}" style="color:#406546">{html.escape(inquiry.email or '')}</a></td></tr>
      <tr style="background:#fafaf8"><td style="padding:10px 12px;color:#7a766d">Phone</td>
          <td style="padding:10px 12px">{html.escape(inquiry.phone or '—')}</td></tr>
      <tr><td style="padding:10px 12px;color:#7a766d">Country</td>
          <td style="padding:10px 12px">{html.escape(inquiry.country or '—')}</td></tr>
      <tr style="background:#fafaf8"><td style="padding:10px 12px;color:#7a766d">Quantity</td>
          <td style="padding:10px 12px;font-weight:600;color:#406546">{html.escape(str(inquiry.quantity))} kg</td></tr>
      <tr><td style="padding:10px 12px;color:#7a766d">Business Type</td>
          <td style="padding:10px 12px">{html.escape(inquiry.use_case or '—')}</td></tr>
    </table>
    {"<div style='margin-top:20px;padding:16px;background:#f9f0e2;border-radius:12px'><p style='margin:0 0 4px;font-size:12px;color:#7a766d'>Message</p><p style='margin:0;font-size:14px;line-height:1.6'>" + html.escape(inquiry.message) + "</p></div>" if inquiry.message else ""}
  </div>
</div>"""

        result = await send_email(
            to=RECIPIENT,
            subject=f"New Wholesale Inquiry from {html.escape(inquiry.company or '')}",
            html=html_body,
            from_email="NAKAI Wholesale <wholesale@nakaiinfo.com>",
            reply_to=inquiry.email,
        )
        if result:
            logger.info(f"Inquiry notification sent for {inquiry.company}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to send inquiry notification: {e}")
        return False


async def send_contact_inquiry_notification(inquiry) -> bool:
    """Send an email notification for a new contact page inquiry via Resend."""
    try:
        from services.resend_client import send_email

        type_label = getattr(inquiry, 'inquiry_type', 'General')
        subject = f"New {html.escape(type_label)} Inquiry from {html.escape(getattr(inquiry, 'name', 'Website'))}"

        # Build details rows
        rows = []
        if getattr(inquiry, 'name', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px;width:120px">Name</td><td style="padding:8px 16px;font-size:14px">{html.escape(inquiry.name)}</td></tr>')
        if getattr(inquiry, 'email', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Email</td><td style="padding:8px 16px;font-size:14px"><a href="mailto:{html.escape(inquiry.email)}">{html.escape(inquiry.email)}</a></td></tr>')
        if getattr(inquiry, 'company', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Company</td><td style="padding:8px 16px;font-size:14px">{html.escape(inquiry.company)}</td></tr>')
        if getattr(inquiry, 'phone', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Phone</td><td style="padding:8px 16px;font-size:14px">{html.escape(inquiry.phone)}</td></tr>')
        if getattr(inquiry, 'business_type', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Business Type</td><td style="padding:8px 16px;font-size:14px">{html.escape(inquiry.business_type)}</td></tr>')
        if getattr(inquiry, 'monthly_volume', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Monthly Volume</td><td style="padding:8px 16px;font-size:14px">{html.escape(str(inquiry.monthly_volume))}</td></tr>')
        dates = getattr(inquiry, 'preferred_dates', None)
        if dates:
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px">Preferred Dates</td><td style="padding:8px 16px;font-size:14px">{html.escape(", ".join(dates))}</td></tr>')
        if getattr(inquiry, 'message', ''):
            rows.append(f'<tr><td style="padding:8px 16px;color:#6e6e73;font-size:13px;vertical-align:top">Message</td><td style="padding:8px 16px;font-size:14px;white-space:pre-wrap">{html.escape(inquiry.message)}</td></tr>')

        rows_html = ''.join(rows)
        html_body = (
            '<div style="font-family:\'Work Sans\',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">'
            '<div style="background:#406546;padding:24px 32px;border-radius:16px 16px 0 0;text-align:center">'
            f'<h2 style="color:#fff;margin:0;font-size:18px;font-weight:600">New {html.escape(type_label)} Inquiry</h2>'
            '</div>'
            '<div style="background:#fff;padding:32px;border:1px solid #e8e8e8;border-top:none;border-radius:0 0 16px 16px">'
            f'<table style="width:100%;border-collapse:collapse;font-size:14px">{rows_html}</table>'
            '</div>'
            '</div>'
        )

        # Determine recipient based on inquiry type
        to_email = "wholesale@nakaiinfo.com" if type_label == "Wholesale" else "contact@nakaiinfo.com"

        result = await send_email(
            to=to_email,
            subject=subject,
            html=html_body,
            from_email="NAKAI <wholesale@nakaiinfo.com>",
            reply_to=getattr(inquiry, 'email', 'contact@nakaiinfo.com'),
        )
        if result:
            logger.info(f"Contact inquiry notification sent to {to_email}")
            return True
        return False
    except Exception as e:
        logger.warning(f"Failed to send contact inquiry email: {e}")
        return False


async def send_inquiry_auto_reply(inquiry) -> bool:
    """Send auto-reply confirmation to the person who submitted the inquiry."""
    try:
        from services.resend_client import send_email

        name = inquiry.name.split()[0] if inquiry.name else "there"

        html = f"""\
<div style="font-family:'Work Sans',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <div style="background:#406546;padding:32px;border-radius:16px 16px 0 0;text-align:center">
    <img src="https://nakaimatcha.com/cdn/shop/files/nakai-logo-white.png" alt="NAKAI" style="height:28px;margin-bottom:12px" />
    <h2 style="color:#fff;margin:0;font-size:20px;font-weight:600">Thank you for your inquiry</h2>
  </div>
  <div style="background:#fff;padding:32px;border:1px solid #e8e8e8;border-top:none;border-radius:0 0 16px 16px">
    <p style="font-size:15px;line-height:1.7;color:#333">Hi {html.escape(name)},</p>
    <p style="font-size:15px;line-height:1.7;color:#333">Thank you for your interest in NAKAI Matcha wholesale partnership. We've received your inquiry and our team will review it carefully. Complimentary samples are available at no cost — please don't hesitate to request them.</p>
    <p style="font-size:15px;line-height:1.7;color:#333"><strong>What happens next:</strong></p>
    <ul style="font-size:14px;line-height:1.8;color:#555;padding-left:20px">
      <li>Our wholesale team will review your requirements within <strong>1-2 business days</strong></li>
      <li>We'll prepare a <strong>tailored pricing proposal</strong> based on your volume</li>
      <li>We can arrange <strong>complimentary samples</strong> for quality evaluation</li>
    </ul>
    <div style="margin:28px 0;padding:20px;background:#f9f6f0;border-radius:12px">
      <p style="margin:0 0 8px;font-size:13px;color:#7a766d;font-weight:500">YOUR INQUIRY SUMMARY</p>
      <p style="margin:0;font-size:14px;color:#333">
        <strong>{html.escape(inquiry.company or '')}</strong><br>
        Volume: {html.escape(str(inquiry.quantity))} kg{(' · ' + html.escape(inquiry.use_case)) if inquiry.use_case else ''}
        {(' · ' + html.escape(inquiry.country)) if inquiry.country else ''}
      </p>
    </div>
    <div style="margin:28px 0;padding:20px;background:#f9f6f0;border-radius:12px;border-left:3px solid #406546">
      <p style="margin:0 0 8px;font-size:13px;color:#7a766d;font-weight:500">PARTNER RESULTS</p>
      <p style="margin:0;font-size:14px;color:#333;line-height:1.7">Many of our wholesale partners — even small cafes — sell over <strong>3,000 cups per month</strong>. The reason: our matcha is the same grade we use in actual tea ceremonies, so you can confidently call it <strong>ceremonial grade</strong>. We also provide recipe development support and hands-on guidance for preparing matcha-based drinks.</p>
    </div>
    <div style="text-align:center;margin:28px 0">
      <a href="https://nakaimatcha.com/collections/matcha-wholesale" style="display:inline-block;background:#406546;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:600;font-size:14px">Browse Our Wholesale Collection</a>
    </div>
    <p style="font-size:14px;line-height:1.6;color:#555">In the meantime, feel free to reply to this email or contact us directly at <a href="mailto:wholesale@nakaiinfo.com" style="color:#406546">wholesale@nakaiinfo.com</a></p>
    <hr style="border:none;border-top:1px solid #eee;margin:24px 0" />
    <p style="font-size:12px;color:#999;text-align:center">
      NAKAI Matcha · Premium Organic Matcha from Kagoshima, Japan<br>
      <a href="https://nakaimatcha.com" style="color:#999">nakaimatcha.com</a>
    </p>
  </div>
</div>"""

        result = await send_email(
            to=inquiry.email,
            subject="Thank you for your NAKAI wholesale inquiry",
            html=html,
            from_email="NAKAI Wholesale <wholesale@nakaiinfo.com>",
            reply_to="wholesale@nakaiinfo.com",
        )
        if result:
            logger.info(f"Auto-reply sent to {inquiry.email}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to send auto-reply: {e}")
        return False


async def send_followup_day2(inquiry) -> bool:
    """Day 2 follow-up: Did you have questions?"""
    try:
        from services.resend_client import send_email
        name = inquiry.get("name", "").split()[0] if inquiry.get("name") else "there"

        html = f"""\
<div style="font-family:'Work Sans',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <div style="padding:32px">
    <img src="https://nakaimatcha.com/cdn/shop/files/nakai-logo-white.png" alt="NAKAI" style="height:22px;margin-bottom:24px;filter:brightness(0)" />
    <p style="font-size:15px;line-height:1.7;color:#333">Hi {html.escape(name)},</p>
    <p style="font-size:15px;line-height:1.7;color:#333">Just checking in — our team is reviewing your wholesale inquiry for <strong>{html.escape(inquiry.get('company', 'your business'))}</strong>.</p>
    <p style="font-size:15px;line-height:1.7;color:#333">While we prepare your proposal, here are a few things that might be helpful:</p>
    <ul style="font-size:14px;line-height:1.8;color:#555;padding-left:20px">
      <li><strong>Free samples</strong> — We're happy to send complimentary matcha samples so you can evaluate quality firsthand</li>
      <li><strong>Menu consultation</strong> — Our team can help develop matcha menu items tailored to your concept</li>
      <li><strong>Flexible MOQ</strong> — Starting from just 10 kg for first orders</li>
    </ul>
    <p style="font-size:15px;line-height:1.7;color:#333">Any questions? Simply reply to this email.</p>
    <p style="font-size:14px;line-height:1.6;color:#555;margin-top:24px">Best regards,<br><strong>NAKAI Wholesale Team</strong></p>
    <hr style="border:none;border-top:1px solid #eee;margin:24px 0" />
    <p style="font-size:12px;color:#999;text-align:center">NAKAI Matcha · <a href="https://nakaimatcha.com" style="color:#999">nakaimatcha.com</a></p>
  </div>
</div>"""

        result = await send_email(
            to=inquiry.get("email", ""),
            subject="Your NAKAI wholesale inquiry — any questions?",
            html=html,
            reply_to="wholesale@nakaiinfo.com",
        )
        return bool(result)
    except Exception as e:
        logger.error(f"Day-2 follow-up failed: {e}")
        return False


async def send_followup_day7(inquiry) -> bool:
    """Day 7 follow-up: Partner spotlight + last touch."""
    try:
        from services.resend_client import send_email
        name = inquiry.get("name", "").split()[0] if inquiry.get("name") else "there"

        html = f"""\
<div style="font-family:'Work Sans',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <div style="padding:32px">
    <img src="https://nakaimatcha.com/cdn/shop/files/nakai-logo-white.png" alt="NAKAI" style="height:22px;margin-bottom:24px;filter:brightness(0)" />
    <p style="font-size:15px;line-height:1.7;color:#333">Hi {html.escape(name)},</p>
    <p style="font-size:15px;line-height:1.7;color:#333">I wanted to share how some of our partners are using NAKAI matcha:</p>
    <div style="margin:20px 0;padding:20px;background:#f9f6f0;border-radius:12px">
      <p style="margin:0 0 8px;font-size:14px;color:#406546;font-weight:600">☕ Comet Over Delphi — Los Angeles</p>
      <p style="margin:0;font-size:13px;color:#555;line-height:1.6">"NAKAI's SHI (4) has become our best-selling matcha latte. The consistency across batches is what we needed for daily volume."</p>
    </div>
    <div style="margin:20px 0;padding:20px;background:#f9f6f0;border-radius:12px">
      <p style="margin:0 0 8px;font-size:14px;color:#406546;font-weight:600">🍵 Ohill — Kyoto</p>
      <p style="margin:0;font-size:13px;color:#555;line-height:1.6">"The MQP grading system gives us confidence in exactly what we're sourcing. Our customers notice the difference."</p>
    </div>
    <p style="font-size:15px;line-height:1.7;color:#333;margin-top:20px">If you'd like to discuss your specific needs or request samples, just reply to this email. We're here to help.</p>
    <div style="text-align:center;margin:28px 0">
      <a href="https://nakaimatcha.com/collections/matcha-wholesale" style="display:inline-block;background:#406546;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:600;font-size:14px">View Wholesale Products</a>
    </div>
    <p style="font-size:14px;line-height:1.6;color:#555">Warm regards,<br><strong>Akira Nagasawa</strong><br>Founder, NAKAI Matcha</p>
    <hr style="border:none;border-top:1px solid #eee;margin:24px 0" />
    <p style="font-size:12px;color:#999;text-align:center">NAKAI Matcha · <a href="https://nakaimatcha.com" style="color:#999">nakaimatcha.com</a></p>
  </div>
</div>"""

        result = await send_email(
            to=inquiry.get("email", ""),
            subject="How cafes use NAKAI matcha — partner stories",
            html=html,
            reply_to="wholesale@nakaiinfo.com",
        )
        return bool(result)
    except Exception as e:
        logger.error(f"Day-7 follow-up failed: {e}")
        return False

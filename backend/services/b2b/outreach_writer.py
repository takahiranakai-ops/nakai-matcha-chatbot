"""B2B Outreach Writer — Claude-powered personalized sales emails.

Virtual Team Members #15-20: Copywriters.
Generates 3-step email sequences tailored to each café.
"""

import logging

from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the wholesale outreach specialist for NAKAI, a premium organic matcha brand from Kagoshima, Japan.

## Brand
NAKAI produces ceremonial and culinary grade organic matcha, grown in Kagoshima's volcanic soil.
Wholesale pricing: $25-45/100g depending on grade and volume.
Free samples available for qualified cafés.
Website: https://nakaimatcha.com

## Tone
- Professional but warm — like a knowledgeable friend, not a salesperson
- Brief and respectful of busy café owners' time
- Genuinely helpful — focus on how matcha can boost their menu and margins
- Subtle Japanese aesthetic — clean, refined

## Rules
- Keep emails SHORT (under 150 words for initial, under 120 for follow-ups)
- One clear call-to-action per email
- Never be pushy or use aggressive sales language
- Always include the unsubscribe notice placeholder: {{unsubscribe_link}}
- Personalize based on the café's name, city, and type
- Output ONLY the HTML email body. No subject line. No markdown fences.
- Use simple, clean HTML. Inline styles only. Max-width 600px.
- Brand colors: #406546 (green), #F9F0E2 (cream)
- Font: Work Sans or system sans-serif"""

STEP_PROMPTS = {
    1: """Write an initial outreach email to {cafe_name}, a {cafe_type} in {city}.
Introduce NAKAI matcha briefly and offer free samples.
CTA: Reply to request samples.""",

    2: """Write a follow-up email to {cafe_name} in {city}.
They received our initial email 5 days ago but haven't replied.
Share a quick fact about matcha's growing popularity and profit margins for cafés.
CTA: Reply to schedule a quick call or request samples.""",

    3: """Write a final outreach email to {cafe_name} in {city}.
This is the last email in the sequence. Keep it brief and gracious.
Mention a limited-time wholesale discount (15% off first order).
CTA: Reply within 7 days to claim the offer. No pressure.""",
}


async def generate_outreach_email(
    lead: dict,
    step: int = 1,
) -> dict:
    """Generate a personalized outreach email for a lead.

    Returns: {"subject": str, "html": str}
    """
    cafe_name = lead.get("name", "your café")
    city = lead.get("city", "your city")
    cafe_type = lead.get("cafe_type", "café")

    step_prompt = STEP_PROMPTS.get(step, STEP_PROMPTS[1])
    user_prompt = step_prompt.format(
        cafe_name=cafe_name,
        city=city,
        cafe_type=cafe_type,
    )

    # Generate subject line
    subjects = {
        1: f"Premium organic matcha for {cafe_name}",
        2: f"Following up — free matcha samples for {cafe_name}",
        3: f"Last chance: 15% off wholesale matcha for {cafe_name}",
    }
    subject = subjects.get(step, subjects[1])

    if not settings.anthropic_api_key:
        logger.warning("Anthropic API key not configured, using fallback")
        return {"subject": subject, "html": _fallback_email(lead, step)}

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        html = response.content[0].text
        # Strip markdown fences if present
        import re
        html = re.sub(r'^```html?\s*\n?', '', html)
        html = re.sub(r'\n?```\s*$', '', html)
        return {"subject": subject, "html": html.strip()}
    except Exception as e:
        logger.error(f"[B2B] Claude outreach generation failed: {e}")
        return {"subject": subject, "html": _fallback_email(lead, step)}


async def generate_batch(leads_with_steps: list[tuple[dict, int]]) -> list[dict]:
    """Generate emails for multiple leads. Returns list of {lead_id, subject, html, step}."""
    results = []
    for lead, step in leads_with_steps:
        email = await generate_outreach_email(lead, step)
        results.append({
            "lead_id": lead["id"],
            "subject": email["subject"],
            "html": email["html"],
            "step": step,
        })
    return results


def _fallback_email(lead: dict, step: int) -> str:
    """Simple fallback template when Claude API is unavailable."""
    name = lead.get("name", "there")
    city = lead.get("city", "")
    loc = f" in {city}" if city else ""

    if step == 1:
        body = f"""Hi {name} team,

I'm Takahiro from NAKAI — we produce organic ceremonial matcha in Kagoshima, Japan.

I noticed your café{loc} and thought our matcha could be a great addition to your menu. We'd love to send you free samples to try.

Would you be interested? Just reply and I'll get them shipped out.

Best regards,
Takahiro Nakai"""
    elif step == 2:
        body = f"""Hi {name} team,

Following up on my email from a few days ago. Matcha drinks are one of the fastest-growing menu categories — cafés adding matcha see 20-30% higher margins compared to coffee drinks.

I'd love to send you a free sample kit. No commitment needed.

Best,
Takahiro"""
    else:
        body = f"""Hi {name} team,

Last note from me — I wanted to offer you 15% off your first wholesale order as a thank-you for considering NAKAI matcha.

This offer is good for the next 7 days. If now isn't the right time, no worries at all.

Warm regards,
Takahiro Nakai"""

    return f"""<div style="max-width:600px;margin:0 auto;font-family:Work Sans,system-ui,sans-serif;color:#333;line-height:1.7;padding:40px 24px;">
<p style="white-space:pre-line;font-size:15px;">{body}</p>
<hr style="border:none;border-top:1px solid #eee;margin:32px 0 16px;">
<p style="font-size:11px;color:#999;text-align:center;">
  NAKAI · Kagoshima, Japan · <a href="https://nakaimatcha.com" style="color:#406546;">nakaimatcha.com</a><br>
  <a href="{{{{unsubscribe_link}}}}" style="color:#999;">Unsubscribe</a>
</p>
</div>"""

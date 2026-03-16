"""B2B Outreach Writer — Uses custom templates or Claude for sales emails.

Virtual Team Members #15-20: Copywriters.
Generates 3-step email sequences tailored to each cafe.
Priority: DB templates > Claude AI > fallback.
"""

import logging
import re

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

# Used when no DB template and no Claude API
FALLBACK_TEMPLATES = {
    1: {
        "subject": "Premium organic matcha for {{cafe_name}}",
        "body": """Hi {{cafe_name}} team,

I'm Takahiro from NAKAI — we produce organic ceremonial matcha in Kagoshima, Japan.

I noticed your cafe{{location}} and thought our matcha could be a great addition to your menu. We'd love to send you free samples to try.

Would you be interested? Just reply and I'll get them shipped out.

Best regards,
Takahiro Nakai""",
    },
    2: {
        "subject": "Following up — free matcha samples for {{cafe_name}}",
        "body": """Hi {{cafe_name}} team,

Following up on my email from a few days ago. Matcha drinks are one of the fastest-growing menu categories — cafes adding matcha see 20-30% higher margins compared to coffee drinks.

I'd love to send you a free sample kit. No commitment needed.

Best,
Takahiro""",
    },
    3: {
        "subject": "Last chance: 15% off wholesale matcha for {{cafe_name}}",
        "body": """Hi {{cafe_name}} team,

Last note from me — I wanted to offer you 15% off your first wholesale order as a thank-you for considering NAKAI matcha.

This offer is good for the next 7 days. If now isn't the right time, no worries at all.

Warm regards,
Takahiro Nakai""",
    },
}

# Claude system prompt (used only when no custom template is set)
CLAUDE_SYSTEM = """You are the wholesale outreach specialist for NAKAI, a premium organic matcha brand from Kagoshima, Japan.

## Brand
NAKAI produces ceremonial and culinary grade organic matcha, grown in Kagoshima's volcanic soil.
Wholesale pricing: $25-45/100g depending on grade and volume.
Free samples available for qualified cafes.
Website: https://nakaimatcha.com

## Tone
- Professional but warm
- Brief and respectful of busy cafe owners' time
- Genuinely helpful
- Subtle Japanese aesthetic

## Rules
- Keep emails SHORT (under 150 words)
- One clear call-to-action per email
- Never be pushy
- Always include {{unsubscribe_link}} placeholder
- Output ONLY the HTML email body. No subject line. No markdown fences.
- Use simple, clean HTML. Inline styles only. Max-width 600px.
- Brand colors: #406546 (green), #F9F0E2 (cream)"""

CLAUDE_STEP_PROMPTS = {
    1: "Write an initial outreach email to {cafe_name}, a {cafe_type} in {city}. "
       "Introduce NAKAI matcha and offer free samples. CTA: Reply to request samples.",
    2: "Write a follow-up email to {cafe_name} in {city}. "
       "They received our initial email 5 days ago but haven't replied. "
       "Share matcha's growing popularity and profit margins. CTA: Reply or request samples.",
    3: "Write a final outreach email to {cafe_name} in {city}. "
       "Keep it brief and gracious. Mention 15% off first order. "
       "CTA: Reply within 7 days. No pressure.",
}


async def _get_db_template(step: int) -> dict | None:
    """Fetch custom template from DB if user has set one."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_sequences",
            headers=supabase_client._HEADERS,
            params={
                "step_number": f"eq.{step}",
                "name": "eq.Default",
                "is_active": "eq.true",
                "limit": "1",
            },
        )
        rows = resp.json()
        if rows and rows[0].get("body_template") and len(rows[0]["body_template"]) > 30:
            return {
                "subject": rows[0].get("subject_template", ""),
                "body": rows[0].get("body_template", ""),
            }
    except Exception as e:
        logger.debug(f"[B2B] DB template fetch failed: {e}")
    return None


def _apply_variables(text: str, lead: dict) -> str:
    """Replace {{cafe_name}}, {{city}}, {{cafe_type}}, {{location}} in template."""
    cafe_name = lead.get("name", "your cafe")
    city = lead.get("city", "")
    cafe_type = lead.get("cafe_type", "cafe")
    location = f" in {city}" if city else ""

    text = text.replace("{{cafe_name}}", cafe_name)
    text = text.replace("{{city}}", city)
    text = text.replace("{{cafe_type}}", cafe_type)
    text = text.replace("{{location}}", location)
    return text


def _wrap_html(body_text: str) -> str:
    """Wrap plain text body in clean HTML email template."""
    escaped = body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<div style="max-width:600px;margin:0 auto;font-family:Work Sans,system-ui,sans-serif;color:#333;line-height:1.7;padding:40px 24px;">
<p style="white-space:pre-line;font-size:15px;">{escaped}</p>
<hr style="border:none;border-top:1px solid #eee;margin:32px 0 16px;">
<p style="font-size:11px;color:#999;text-align:center;">
  NAKAI &middot; Kagoshima, Japan &middot; <a href="https://nakaimatcha.com" style="color:#406546;">nakaimatcha.com</a><br>
  <a href="{{{{unsubscribe_link}}}}" style="color:#999;">Unsubscribe</a>
</p>
</div>"""


async def generate_outreach_email(lead: dict, step: int = 1) -> dict:
    """Generate a personalized outreach email for a lead.

    Priority:
    1. Custom template from DB (user-written)
    2. Claude AI generation
    3. Hardcoded fallback

    Returns: {"subject": str, "html": str}
    """
    # 1. Check for custom DB template
    db_tpl = await _get_db_template(step)
    if db_tpl:
        subject = _apply_variables(db_tpl["subject"], lead)
        body = _apply_variables(db_tpl["body"], lead)
        # If body looks like HTML, use directly; otherwise wrap
        if "<" in body and ">" in body and ("div" in body.lower() or "p" in body.lower()):
            return {"subject": subject, "html": body}
        return {"subject": subject, "html": _wrap_html(body)}

    # 2. Try Claude AI
    if settings.anthropic_api_key:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

            cafe_name = lead.get("name", "your cafe")
            city = lead.get("city", "your city")
            cafe_type = lead.get("cafe_type", "cafe")

            prompt = CLAUDE_STEP_PROMPTS.get(step, CLAUDE_STEP_PROMPTS[1])
            user_prompt = prompt.format(
                cafe_name=cafe_name, city=city, cafe_type=cafe_type,
            )

            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=CLAUDE_SYSTEM,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.7,
            )
            html = response.content[0].text
            html = re.sub(r'^```html?\s*\n?', '', html)
            html = re.sub(r'\n?```\s*$', '', html)

            subjects = {
                1: f"Premium organic matcha for {cafe_name}",
                2: f"Following up — free matcha samples for {cafe_name}",
                3: f"Last chance: 15% off wholesale matcha for {cafe_name}",
            }
            return {"subject": subjects.get(step, subjects[1]), "html": html.strip()}
        except Exception as e:
            logger.error(f"[B2B] Claude generation failed: {e}")

    # 3. Fallback
    tpl = FALLBACK_TEMPLATES.get(step, FALLBACK_TEMPLATES[1])
    subject = _apply_variables(tpl["subject"], lead)
    body = _apply_variables(tpl["body"], lead)
    return {"subject": subject, "html": _wrap_html(body)}


async def generate_batch(leads_with_steps: list[tuple[dict, int]]) -> list[dict]:
    """Generate emails for multiple leads."""
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

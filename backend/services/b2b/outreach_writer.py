"""B2B Outreach Writer — Segment-aware email generation.

Virtual Team Members #15-20: Copywriters.
Generates 3-step email sequences tailored to each segment (cafe, hotel, restaurant).
Priority: DB templates > Claude AI > fallback.
"""

import logging
import re
from typing import Optional

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

_anthropic_client: Optional["anthropic.AsyncAnthropic"] = None


def _get_anthropic_client() -> "anthropic.AsyncAnthropic":
    """Return a module-level Anthropic client (created once)."""
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _anthropic_client


def _sanitize_email_html(html_content: str) -> str:
    """Remove dangerous tags from LLM-generated HTML content."""
    html_content = re.sub(
        r'<(script|iframe|object|embed|form)[^>]*>.*?</\1>',
        '', html_content, flags=re.DOTALL | re.IGNORECASE,
    )
    html_content = re.sub(
        r'<(script|iframe|object|embed|form)[^>]*/>',
        '', html_content, flags=re.IGNORECASE,
    )
    # Remove event handlers
    html_content = re.sub(
        r'\s+on\w+\s*=\s*["\'][^"\']*["\']',
        '', html_content, flags=re.IGNORECASE,
    )
    # Remove javascript: URLs
    html_content = re.sub(
        r'href\s*=\s*["\']javascript:[^"\']*["\']',
        'href="#"', html_content, flags=re.IGNORECASE,
    )
    return html_content

# ── Fallback Templates (per segment × step) ────────────────

FALLBACK_TEMPLATES: dict[str, dict[int, dict]] = {
    "cafe": {
        1: {
            "subject": "Premium organic matcha for {{cafe_name}}",
            "body": """Hi {{cafe_name}} team,

I'm Takahiro from NAKAI — we produce organic ceremonial matcha in Kagoshima, Japan.

I noticed your cafe{{location}} and thought our matcha could be a great addition to your menu. Cafes adding matcha see 20-30% higher margins compared to coffee drinks.

We'd love to send you free samples to try. Just reply and I'll get them shipped out.

Best regards,
Takahiro Nakai""",
        },
        2: {
            "subject": "Following up — free matcha samples for {{cafe_name}}",
            "body": """Hi {{cafe_name}} team,

Following up on my email from a few days ago. Matcha is one of the fastest-growing menu categories — and our organic ceremonial grade is sourced directly from Kagoshima's volcanic soil.

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
    },
    "luxury_hotel": {
        1: {
            "subject": "Elevate your guest experience with Japanese matcha — {{cafe_name}}",
            "body": """Dear {{cafe_name}} team,

I'm Takahiro from NAKAI, a premium organic matcha producer based in Kagoshima, Japan.

I believe our ceremonial-grade matcha could be a wonderful addition to your guest experience — whether as a signature lobby lounge beverage, a wellness amenity, or an in-room welcome offering.

Leading luxury hotels are embracing authentic Japanese matcha as a way to differentiate their F&B program. I'd love to send a complimentary tasting kit for your team to explore.

Would you be open to trying it?

Best regards,
Takahiro Nakai""",
        },
        2: {
            "subject": "How luxury hotels are using matcha — {{cafe_name}}",
            "body": """Dear {{cafe_name}} team,

Following up on my recent email. The wellness hospitality trend continues to grow, and matcha is at the center — rich in antioxidants, naturally energizing, and visually stunning.

Our matcha is organic, stone-ground in Kagoshima, and perfect for high-end presentations. I'd love to send a complimentary tasting for your F&B team.

No commitment — just a chance to experience the quality firsthand.

Best,
Takahiro""",
        },
        3: {
            "subject": "Complimentary matcha tasting for your team — {{cafe_name}}",
            "body": """Dear {{cafe_name}} team,

Last note from me — I'd love to arrange a complimentary matcha tasting for your F&B or wellness team. Our clients include boutique hotels looking to offer something truly special to their guests.

If the timing isn't right, I completely understand. Wishing you a wonderful season ahead.

Warm regards,
Takahiro Nakai""",
        },
    },
    "fine_dining": {
        1: {
            "subject": "Kagoshima matcha for your culinary program — {{cafe_name}}",
            "body": """Dear Chef and {{cafe_name}} team,

I'm Takahiro from NAKAI — we produce organic ceremonial matcha in Kagoshima, Japan, where volcanic soil and ocean mist create exceptional flavor.

I thought our matcha could inspire your culinary program — whether for a signature dessert course, a creative cocktail, or an elevated tea pairing. Our matcha has deep umami notes that pair beautifully with fine cuisine.

I'd love to send a chef's sample kit for you to experiment with.

Best regards,
Takahiro Nakai""",
        },
        2: {
            "subject": "Matcha beyond dessert — creative ideas for {{cafe_name}}",
            "body": """Dear {{cafe_name}} team,

Following up on my recent note. Beyond classic desserts, top restaurants are using matcha in savory glazes, cocktail programs, and amuse-bouche presentations.

Our stone-ground organic matcha from Kagoshima offers a rich, complex umami that stands up to sophisticated flavor profiles. I'd love to send samples for your team to explore.

Best,
Takahiro""",
        },
        3: {
            "subject": "Chef's matcha sample kit for {{cafe_name}}",
            "body": """Dear {{cafe_name}} team,

Last note from me — I'd love to send a complimentary chef's sample kit with our ceremonial and culinary grades, plus a few recipe inspirations.

If the timing isn't right for your current menu cycle, no worries at all. Wishing you continued success.

Warm regards,
Takahiro Nakai""",
        },
    },
}

# ── Claude AI Prompts (per segment × step) ─────────────────

CLAUDE_SYSTEM = """You are the wholesale outreach specialist for NAKAI, a premium organic matcha brand from Kagoshima, Japan.

## Brand
NAKAI produces ceremonial and culinary grade organic matcha, grown in Kagoshima's volcanic soil.
Wholesale pricing: $25-45/100g depending on grade and volume.
Free samples available for qualified businesses.
Website: https://nakaimatcha.com

## Tone
- Professional but warm
- Brief and respectful of busy decision-makers' time
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

CLAUDE_SEGMENT_CONTEXT = {
    "cafe": "This is a specialty cafe. Focus on menu differentiation, higher margins than coffee, and trendy appeal.",
    "luxury_hotel": "This is a luxury hotel. Focus on guest experience, wellness amenity, lobby lounge offering, and premium brand positioning.",
    "fine_dining": "This is a fine dining restaurant. Focus on culinary creativity, terroir story, flavor pairing, and chef-level quality.",
}

CLAUDE_STEP_PROMPTS: dict[str, dict[int, str]] = {
    "cafe": {
        1: "Write an initial outreach email to {name}, a {segment_label} in {city}. Introduce NAKAI matcha and offer free samples. CTA: Reply to request samples.",
        2: "Write a follow-up to {name} in {city}. They received our initial email but haven't replied. Share matcha's growing popularity and profit margins. CTA: Reply or request samples.",
        3: "Write a final outreach to {name} in {city}. Keep it brief and gracious. Mention 15% off first order. CTA: Reply within 7 days.",
    },
    "luxury_hotel": {
        1: "Write an initial outreach email to {name}, a {segment_label} in {city}. Propose matcha for guest experience — lobby lounge, wellness, in-room amenity. CTA: Reply to receive complimentary tasting.",
        2: "Write a follow-up to {name} in {city}. Share how luxury hotels use matcha for wellness and differentiation. CTA: Arrange team tasting.",
        3: "Write a final outreach to {name} in {city}. Offer complimentary tasting for F&B team. Keep gracious. CTA: Reply to schedule.",
    },
    "fine_dining": {
        1: "Write an initial outreach email to {name}, a {segment_label} in {city}. Position matcha for culinary program — dessert, cocktail, pairing. CTA: Reply to receive chef's sample kit.",
        2: "Write a follow-up to {name} in {city}. Share creative matcha uses beyond dessert — savory, cocktails, amuse-bouche. CTA: Request samples.",
        3: "Write a final outreach to {name} in {city}. Offer chef's sample kit with recipe inspirations. Keep gracious. CTA: Reply to receive kit.",
    },
}


# ── Template Fetching ───────────────────────────────────────

async def _get_db_template(step: int, segment: str = "cafe") -> dict | None:
    """Fetch custom template from DB by segment + step.

    Falls back to 'Default' name for backward compatibility.
    """
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        # Try segment-specific template first
        for name in (segment, "Default"):
            resp = await client.get(
                f"{supabase_client._BASE_URL}/b2b_sequences",
                headers=supabase_client._HEADERS,
                params={
                    "step_number": f"eq.{step}",
                    "name": f"eq.{name}",
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
    """Replace template variables with lead data."""
    name = lead.get("name", "your business")
    city = lead.get("city", "")
    cafe_type = lead.get("cafe_type", "cafe")
    location = f" in {city}" if city else ""

    text = text.replace("{{cafe_name}}", name)
    text = text.replace("{{name}}", name)
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


# ── Main Generation ─────────────────────────────────────────

async def generate_outreach_email(lead: dict, step: int = 1) -> dict:
    """Generate a personalized outreach email for a lead.

    Determines segment from lead['cafe_type'].
    Priority: DB template > Claude AI > hardcoded fallback.
    """
    segment = lead.get("cafe_type", "cafe")
    if segment not in FALLBACK_TEMPLATES:
        segment = "cafe"

    # 1. Check for custom DB template
    db_tpl = await _get_db_template(step, segment)
    if db_tpl:
        subject = _apply_variables(db_tpl["subject"], lead)
        body = _apply_variables(db_tpl["body"], lead)
        if "<" in body and ">" in body and ("div" in body.lower() or "p" in body.lower()):
            return {"subject": subject, "html": body}
        return {"subject": subject, "html": _wrap_html(body)}

    # 2. Try Claude AI
    if settings.anthropic_api_key:
        try:
            client = _get_anthropic_client()

            from services.b2b.segments import SEGMENTS
            seg_def = SEGMENTS.get(segment, SEGMENTS["cafe"])
            name = lead.get("name", "your business")
            city = lead.get("city", "your city")

            seg_context = CLAUDE_SEGMENT_CONTEXT.get(segment, "")
            step_prompts = CLAUDE_STEP_PROMPTS.get(segment, CLAUDE_STEP_PROMPTS["cafe"])
            prompt_tpl = step_prompts.get(step, step_prompts[1])
            user_prompt = prompt_tpl.format(
                name=name, city=city, segment_label=seg_def["label_en"],
            )

            system = CLAUDE_SYSTEM + f"\n\n## Segment Context\n{seg_context}"

            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.7,
            )
            html = response.content[0].text
            html = re.sub(r'^```html?\s*\n?', '', html)
            html = re.sub(r'\n?```\s*$', '', html)

            subjects = {
                "cafe": {
                    1: f"Premium organic matcha for {name}",
                    2: f"Following up — free matcha samples for {name}",
                    3: f"Last chance: 15% off wholesale matcha for {name}",
                },
                "luxury_hotel": {
                    1: f"Elevate your guest experience with Japanese matcha — {name}",
                    2: f"How luxury hotels are using matcha — {name}",
                    3: f"Complimentary matcha tasting for your team — {name}",
                },
                "fine_dining": {
                    1: f"Kagoshima matcha for your culinary program — {name}",
                    2: f"Matcha beyond dessert — creative ideas for {name}",
                    3: f"Chef's matcha sample kit for {name}",
                },
            }
            seg_subjects = subjects.get(segment, subjects["cafe"])
            return {"subject": seg_subjects.get(step, seg_subjects[1]), "html": _sanitize_email_html(html.strip())}
        except Exception as e:
            logger.error(f"[B2B] Claude generation failed: {e}")

    # 3. Fallback
    seg_fallbacks = FALLBACK_TEMPLATES.get(segment, FALLBACK_TEMPLATES["cafe"])
    tpl = seg_fallbacks.get(step, seg_fallbacks[1])
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

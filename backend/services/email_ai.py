"""Claude-powered email design generator for NAKAI brand."""

import logging
import re

from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the creative director for NAKAI, a Japanese luxury matcha maison.
Your email designs channel Hermès editorial restraint and Apple spatial clarity.

## Design Philosophy
- EXTREME white space. Let every element breathe. 60%+ of the email should be empty space
- One idea per scroll. Never crowd
- Typography IS the design. Large, light-weight headlines. Small, quiet body text
- Photography speaks louder than words — one hero image, full-width, no borders
- Colors used surgically: 90% white/cream, 10% brand accent
- No gradients, no patterns, no decorative borders, no icons
- Buttons: minimal, pill-shaped or text-link style. Never chunky
- Footer: whisper-quiet. Almost invisible. Elegant

## Brand Essence
NAKAI is organic matcha from Kagoshima. The brand sits between Aesop and Hermès —
quiet luxury, Japanese precision, nature-rooted.

## Brand Assets
- Logo: {logo_url}
- Primary: {primary_color}
- Background: {secondary_color}
- Text: {text_color}
- Font: {font_family}

## Technical Rules
- HTML tables only (no grid/flexbox). Inline CSS only. Max-width 600px
- Works in Gmail, Apple Mail, Outlook 2019+
- All images: <img> with alt, width, height, style="display:block"

## Editable Blocks
Wrap every user-editable text in:
  data-editable="block-name" data-placeholder="hint"
Example:
  <td data-editable="headline" data-placeholder="Main headline">[Headline]</td>

## Editable Links
Every link the user should customize MUST have:
  data-editable-link="link-name" data-link-placeholder="Where this links to"
Example:
  <a href="#" data-editable-link="cta-link" data-link-placeholder="Product page URL" data-editable="cta-text" data-placeholder="Button text">[Shop Now]</a>

## Structure (top to bottom)
1. **Header**: Logo only. Centered. Generous padding (48px+ top/bottom). White or cream background
2. **Hero Image**: Full-width product photo if provided. No text overlay. Let the image speak
3. **Headline**: One line. Large (28-36px). Light weight (300). Centered. Massive padding around it
4. **Body**: 2-3 short sentences max. Small (14-15px). Muted color. Centered. Line-height 1.8
5. **CTA**: Minimal button OR subtle text link with arrow. Not loud
6. **Footer**: Tiny (11px). Brand name. City. Unsubscribe via {{{{unsubscribe_url}}}}. Nearly transparent gray

## Campaign Photos
{photo_list}

## Rules
- Generate ONLY raw HTML. No explanation. No markdown fences
- Use placeholder text in brackets: [Headline], [Your message], [Shop Now]
- NEVER write actual marketing copy. Only placeholders
- If a hero photo URL is provided, USE IT as the hero image"""


async def generate_email_design(
    description: str,
    brand_assets: dict,
    language: str = "en",
    campaign_photos: list[str] | None = None,
) -> str:
    """Generate branded HTML email template using Claude.

    Args:
        description: User's campaign description
        brand_assets: Dict with logo_url, colors, font_family, photos
        language: "en" or "ja" for placeholder language
        campaign_photos: URLs of photos uploaded for this specific campaign

    Returns:
        HTML string of the email template
    """
    if not settings.anthropic_api_key:
        logger.warning("Anthropic API key not configured, using fallback template")
        return _fallback_template(brand_assets, campaign_photos)

    colors = brand_assets.get("colors", {})

    # Combine brand photos + campaign-specific photos
    all_photos = []
    for p in brand_assets.get("photos", []):
        all_photos.append(f"- Brand: {p.get('label', 'Photo')}: {p.get('url', '')}")
    for url in (campaign_photos or []):
        all_photos.append(f"- Campaign photo (USE AS HERO): {url}")

    photo_list = "\n".join(all_photos) if all_photos else "No photos. Use elegant solid color blocks with generous spacing."

    system = SYSTEM_PROMPT.format(
        logo_url=brand_assets.get("logo_url", ""),
        primary_color=colors.get("primary", "#406546"),
        secondary_color=colors.get("secondary", "#F9F0E2"),
        text_color=colors.get("text", "#1a1a1a"),
        font_family=brand_assets.get("font_family", "Work Sans, Helvetica, Arial, sans-serif"),
        photo_list=photo_list,
    )

    lang_hint = "Japanese" if language == "ja" else "English"
    user_prompt = f"Design an email for: {description}\nPlaceholder language: {lang_hint}"

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        html = response.content[0].text
        html = re.sub(r'^```html?\s*\n?', '', html)
        html = re.sub(r'\n?```\s*$', '', html)
        return html.strip()
    except Exception as e:
        logger.error(f"Claude email generation failed: {e}")
        return _fallback_template(brand_assets, campaign_photos)


def extract_editable_blocks(html: str) -> list[dict]:
    """Extract data-editable text blocks and data-editable-link blocks."""
    blocks = []

    # Text blocks
    pattern = r'data-editable="([^"]+)"[^>]*data-placeholder="([^"]*)"[^>]*>([^<]*)'
    for match in re.finditer(pattern, html):
        blocks.append({
            "type": "text",
            "name": match.group(1),
            "placeholder": match.group(2),
            "current_text": match.group(3).strip(),
        })

    # Link blocks
    link_pattern = r'data-editable-link="([^"]+)"[^>]*data-link-placeholder="([^"]*)"[^>]*href="([^"]*)"'
    for match in re.finditer(link_pattern, html):
        blocks.append({
            "type": "link",
            "name": match.group(1),
            "placeholder": match.group(2),
            "current_url": match.group(3),
        })

    return blocks


def apply_editable_text(html: str, edits: dict[str, str]) -> str:
    """Replace editable block content with user-provided text."""
    for name, text in edits.items():
        pattern = (
            r'(data-editable="' + re.escape(name) + r'"[^>]*>)'
            r'[^<]*'
        )
        html = re.sub(pattern, r'\g<1>' + text, html)
    return html


def apply_editable_links(html: str, link_edits: dict[str, str]) -> str:
    """Replace editable link hrefs with user-provided URLs."""
    for name, url in link_edits.items():
        pattern = (
            r'(data-editable-link="' + re.escape(name) + r'"[^>]*)'
            r'href="[^"]*"'
        )
        html = re.sub(pattern, r'\g<1>href="' + url + '"', html)
    return html


def _fallback_template(brand_assets: dict, campaign_photos: list[str] | None = None) -> str:
    """Hermès-level minimal fallback when Claude API is unavailable."""
    colors = brand_assets.get("colors", {})
    primary = colors.get("primary", "#406546")
    secondary = colors.get("secondary", "#F9F0E2")
    text_color = colors.get("text", "#1a1a1a")
    logo_url = brand_assets.get("logo_url", "")

    logo_html = f'<img src="{logo_url}" alt="NAKAI" width="100" style="display:block;margin:0 auto;">' if logo_url else '<p style="margin:0;font-size:13px;letter-spacing:0.3em;color:{0};text-transform:uppercase;font-weight:400;">NAKAI</p>'.format(text_color)

    hero_html = ""
    if campaign_photos:
        hero_html = f'''<tr><td style="padding:0;">
    <img src="{campaign_photos[0]}" alt="" width="600" style="display:block;width:100%;height:auto;" />
  </td></tr>'''

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:0;background-color:#ffffff;font-family:Work Sans,Helvetica,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#ffffff;">
<tr><td align="center" style="padding:0;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;">

  <tr><td align="center" style="padding:48px 40px 40px;">
    {logo_html}
  </td></tr>

  {hero_html}

  <tr><td align="center" style="padding:56px 60px 24px;">
    <h1 style="margin:0;font-size:32px;font-weight:300;color:{text_color};letter-spacing:0.02em;line-height:1.2;" data-editable="headline" data-placeholder="Main headline">[Headline]</h1>
  </td></tr>

  <tr><td align="center" style="padding:0 80px 48px;">
    <p style="margin:0;font-size:14px;font-weight:300;color:#888;line-height:1.8;" data-editable="body" data-placeholder="Brief message">[Your message here]</p>
  </td></tr>

  <tr><td align="center" style="padding:0 40px 56px;">
    <a href="#" data-editable-link="cta-link" data-link-placeholder="Product page URL" data-editable="cta-text" data-placeholder="Button text" style="display:inline-block;background-color:{primary};color:#ffffff;text-decoration:none;padding:13px 36px;border-radius:24px;font-size:13px;font-weight:400;letter-spacing:0.06em;">[Shop Now]</a>
  </td></tr>

  <tr><td align="center" style="padding:40px;border-top:1px solid #f0f0f0;">
    <p style="margin:0;font-size:11px;color:#bbb;line-height:1.8;">
      NAKAI · Kagoshima, Japan<br>
      <a href="{{{{unsubscribe_url}}}}" style="color:#bbb;text-decoration:underline;">Unsubscribe</a>
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


# ── Newsletter Templates ──────────────────────────────────────

NEWSLETTER_TEMPLATES: dict[str, dict] = {
    "matcha_recipe": {
        "name_ja": "抹茶レシピ",
        "name_en": "Matcha Recipe",
        "prompt": (
            "Create a newsletter featuring a seasonal matcha recipe. "
            "Include a short intro about the season, ingredients list, "
            "step-by-step instructions, and a tip from our tea master. "
            "Keep it warm and approachable for home baristas. "
            "Vary the recipe each time — lattes, smoothies, desserts, savory dishes."
        ),
        "subject_prefix": "This Week's Matcha Recipe",
    },
    "matcha_knowledge": {
        "name_ja": "抹茶知識",
        "name_en": "Matcha Knowledge",
        "prompt": (
            "Create an educational newsletter about matcha. "
            "Pick ONE topic and go deep: matcha grades and how to choose, "
            "health benefits backed by research, the history of tea ceremony, "
            "Kagoshima terroir and volcanic soil, or the stone-grinding process. "
            "Tone: authoritative yet warm. Include one surprising fact."
        ),
        "subject_prefix": "The Art of Matcha",
    },
    "brewing_guide": {
        "name_ja": "点て方ガイド",
        "name_en": "Brewing Guide",
        "prompt": (
            "Create a newsletter with a matcha brewing technique. "
            "Cover ONE method in detail: traditional usucha, koicha thick tea, "
            "iced matcha, matcha latte art, or matcha cocktails. "
            "Include water temperature, ratio, whisking technique, and common mistakes."
        ),
        "subject_prefix": "Matcha Brewing Mastery",
    },
    "seasonal": {
        "name_ja": "季節のご挨拶",
        "name_en": "Seasonal Greeting",
        "prompt": (
            "Create a seasonal greeting newsletter for NAKAI Matcha. "
            "Weave in Japanese seasonal tradition (shun/旬), connect it to matcha culture, "
            "mention what's happening in our Kagoshima tea fields right now, "
            "and include a soft product recommendation."
        ),
        "subject_prefix": "From Kagoshima",
    },
    "wholesale_update": {
        "name_ja": "卸パートナー向け",
        "name_en": "Wholesale Update",
        "prompt": (
            "Create a professional B2B newsletter for wholesale partners. "
            "Cover: seasonal harvest updates, new product grades available, "
            "ordering deadlines, menu inspiration ideas for cafes/restaurants, "
            "and matcha market trends. Professional but warm tone."
        ),
        "subject_prefix": "NAKAI Wholesale Update",
    },
}

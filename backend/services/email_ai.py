"""Claude-powered email design generator for NAKAI brand."""

import logging
import re

import anthropic

from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are NAKAI's email designer. Generate responsive HTML email templates for a premium Japanese matcha brand.

## Brand Identity
- NAKAI is a specialty organic matcha brand from Kagoshima, Japan
- Aesthetic: Refined Japanese minimalism. Clean, spacious, premium
- Never loud or aggressive. Quiet confidence, like the matcha itself

## Technical Requirements
- Responsive HTML email using tables for layout (no CSS grid/flexbox)
- Inline CSS only (no <style> blocks)
- Max width: 600px, centered
- All images use <img> tags with alt text and explicit width/height
- Test-safe: works in Gmail, Apple Mail, Outlook 2019+, Yahoo Mail

## Brand Assets
- Logo URL: {logo_url}
- Primary color: {primary_color}
- Secondary color (background): {secondary_color}
- Accent color: {accent_color}
- Text color: {text_color}
- Font stack: {font_family}

## Editable Text Blocks
Every text area the user should customize MUST be wrapped in a tag with:
  data-editable="block-name"
  data-placeholder="Description of what goes here"
Example:
  <td data-editable="headline" data-placeholder="Main headline">
    [Headline Text]
  </td>

Use descriptive placeholder text inside brackets: [Headline Text], [Your message here], [Product description], etc.

## Required Sections
1. Header: Logo centered
2. Hero: Large visual area with headline
3. Body: 1-3 content blocks
4. CTA: One clear call-to-action button (brand primary color background, white text, rounded corners)
5. Footer: Brand name, unsubscribe link {{{{unsubscribe_url}}}}

## Product Photos Available
{photo_list}

## Do NOT Generate
- The actual copy text (use placeholders)
- Subject line
- Tracking pixels

Generate ONLY the raw HTML. No explanation, no markdown code fences."""


async def generate_email_design(
    description: str,
    brand_assets: dict,
    language: str = "en",
) -> str:
    """Generate branded HTML email template using Claude.

    Args:
        description: User's campaign description (e.g. "Spring new product announcement")
        brand_assets: Dict with logo_url, colors, font_family, photos
        language: "en" or "ja" for placeholder language

    Returns:
        HTML string of the email template
    """
    if not settings.anthropic_api_key:
        logger.warning("Anthropic API key not configured, using fallback template")
        return _fallback_template(brand_assets)

    colors = brand_assets.get("colors", {})
    photos = brand_assets.get("photos", [])
    photo_list = "\n".join(
        f"- {p.get('label', 'Photo')}: {p.get('url', '')}" for p in photos
    ) if photos else "No product photos available. Use solid color blocks instead."

    system = SYSTEM_PROMPT.format(
        logo_url=brand_assets.get("logo_url", ""),
        primary_color=colors.get("primary", "#406546"),
        secondary_color=colors.get("secondary", "#F9F0E2"),
        accent_color=colors.get("accent", "#FFFFFF"),
        text_color=colors.get("text", "#1a1a1a"),
        font_family=brand_assets.get("font_family", "Work Sans, Helvetica, Arial, sans-serif"),
        photo_list=photo_list,
    )

    lang_hint = "Japanese" if language == "ja" else "English"
    user_prompt = f"Design an email for: {description}\nPlaceholder text language: {lang_hint}"

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        html = response.content[0].text

        # Strip markdown fences if Claude wrapped it
        html = re.sub(r'^```html?\s*\n?', '', html)
        html = re.sub(r'\n?```\s*$', '', html)

        return html.strip()
    except Exception as e:
        logger.error(f"Claude email generation failed: {e}")
        return _fallback_template(brand_assets)


def extract_editable_blocks(html: str) -> list[dict]:
    """Extract data-editable blocks from generated HTML.

    Returns list of {"name": str, "placeholder": str, "current_text": str}
    """
    pattern = r'data-editable="([^"]+)"[^>]*data-placeholder="([^"]*)"[^>]*>([^<]*)'
    blocks = []
    for match in re.finditer(pattern, html):
        blocks.append({
            "name": match.group(1),
            "placeholder": match.group(2),
            "current_text": match.group(3).strip(),
        })
    return blocks


def apply_editable_text(html: str, edits: dict[str, str]) -> str:
    """Replace editable block content with user-provided text.

    Args:
        html: Original HTML with data-editable blocks
        edits: Dict of {block_name: new_text}
    """
    for name, text in edits.items():
        # Match the editable element and replace its text content
        pattern = (
            r'(data-editable="' + re.escape(name) + r'"[^>]*>)'
            r'[^<]*'
        )
        html = re.sub(pattern, r'\g<1>' + text, html)
    return html


def _fallback_template(brand_assets: dict) -> str:
    """Simple fallback template when Claude API is unavailable."""
    colors = brand_assets.get("colors", {})
    primary = colors.get("primary", "#406546")
    secondary = colors.get("secondary", "#F9F0E2")
    text_color = colors.get("text", "#1a1a1a")
    logo_url = brand_assets.get("logo_url", "")

    logo_html = f'<img src="{logo_url}" alt="NAKAI" width="120" style="display:block;margin:0 auto;">' if logo_url else '<h1 style="margin:0;color:#fff;font-size:28px;">NAKAI</h1>'

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:0;background-color:{secondary};font-family:Work Sans,Helvetica,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{secondary};">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;">
  <tr><td align="center" style="background-color:{primary};padding:32px 40px;">
    {logo_html}
  </td></tr>
  <tr><td style="padding:40px;" data-editable="headline" data-placeholder="Main headline">
    <h2 style="margin:0 0 16px;color:{text_color};font-size:24px;font-weight:500;">[Headline Text]</h2>
  </td></tr>
  <tr><td style="padding:0 40px 32px;" data-editable="body" data-placeholder="Main message body">
    <p style="margin:0;color:{text_color};font-size:16px;line-height:1.6;">[Your message here]</p>
  </td></tr>
  <tr><td align="center" style="padding:0 40px 40px;">
    <a href="#" style="display:inline-block;background-color:{primary};color:#ffffff;text-decoration:none;padding:14px 32px;border-radius:6px;font-size:16px;font-weight:500;" data-editable="cta" data-placeholder="Call to action text">[Shop Now]</a>
  </td></tr>
  <tr><td align="center" style="padding:24px 40px;border-top:1px solid #eee;color:#999;font-size:12px;">
    NAKAI Matcha | Kagoshima, Japan<br>
    <a href="{{{{unsubscribe_url}}}}" style="color:#999;">Unsubscribe</a>
  </td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

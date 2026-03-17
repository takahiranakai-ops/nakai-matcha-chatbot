"""NAKAI Design Manager — Brand guidelines, asset validation, design review."""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# NAKAI Brand Guidelines (single source of truth)
BRAND_GUIDELINES = {
    "colors": {
        "primary": {"hex": "#406546", "name": "Matcha Green", "usage": "Headers, CTAs, primary brand elements"},
        "secondary": {"hex": "#F9F0E2", "name": "Warm Cream", "usage": "Backgrounds, cards, secondary surfaces"},
        "white": {"hex": "#FFFFFF", "name": "White", "usage": "Text on dark, clean backgrounds"},
        "text_dark": {"hex": "#1D1D1F", "name": "Near Black", "usage": "Body text, headings"},
        "text_secondary": {"hex": "#6E6E73", "name": "Gray", "usage": "Secondary text, captions"},
        "accent_gold": {"hex": "#C4A35A", "name": "Gold", "usage": "Premium accents, badges"},
        "error": {"hex": "#FF3B30", "name": "Red", "usage": "Error states only"},
    },
    "typography": {
        "primary_latin": {"family": "Work Sans", "weights": [400, 500, 600, 700], "usage": "All Latin text"},
        "primary_japanese": {"family": "Shippori Mincho", "weights": [400, 500, 600], "usage": "Japanese text, elegant headings"},
        "sizes": {
            "hero": "48-64px",
            "h1": "32-40px",
            "h2": "24-28px",
            "h3": "20-22px",
            "body": "16-17px",
            "caption": "13-14px",
            "micro": "11-12px",
        },
    },
    "spacing": {
        "unit": "8px",
        "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
        "border_radius": {"small": "8px", "medium": "12px", "large": "16px", "pill": "999px"},
    },
    "photography": {
        "style": "Natural light, warm tones, Japanese minimalism",
        "subjects": ["Matcha preparation", "Tea ceremony", "Uji tea fields", "Portland lifestyle", "Cafe scenes"],
        "avoid": ["Overly saturated colors", "Stock photo feel", "Cluttered compositions"],
    },
    "packaging": {
        "tin": "Matte finish, embossed logo, minimal text",
        "box": "Kraft or cream, single-color print",
        "labels": "Clean typography, Japanese + English bilingual",
        "materials": "Eco-friendly, recyclable where possible",
    },
    "tone_of_voice": {
        "personality": ["Knowledgeable", "Authentic", "Warm", "Premium"],
        "do": ["Lead with education", "Use Japanese terms naturally", "Cite science", "Tell farm stories"],
        "dont": ["Hard sell", "Use clickbait", "Disparage competitors", "Make unsubstantiated health claims"],
    },
}

# Content templates for different platforms
CONTENT_TEMPLATES = {
    "instagram_post": {
        "aspect_ratio": "1:1 or 4:5",
        "text_overlay": "Minimal, bottom 30% of image",
        "font": "Work Sans 600",
        "color_on_photo": "#FFFFFF with slight shadow",
        "hashtags_max": 20,
        "caption_max_chars": 2200,
    },
    "instagram_story": {
        "aspect_ratio": "9:16",
        "brand_elements": "Logo top-left, swipe-up CTA bottom",
        "background": "#406546 or photo with overlay",
    },
    "twitter_post": {
        "max_chars": 280,
        "hashtags_max": 3,
        "tone": "Conversational, educational",
        "include_link": "When relevant to blog or product",
    },
    "blog_article": {
        "hero_image": "16:9 aspect ratio, lifestyle or product",
        "heading_font": "Work Sans 700",
        "body_font": "Work Sans 400",
        "min_words": 800,
        "max_words": 1500,
        "sections": "H2 every 200-300 words",
        "internal_links": "2-3 per article",
    },
    "email_newsletter": {
        "header": "NAKAI logo + matcha green bar",
        "width": "600px max",
        "cta_button": "#406546 background, white text, 12px radius",
        "footer": "Unsubscribe + social links",
    },
    "wholesale_deck": {
        "slides": "Clean white background, matcha green accents",
        "fonts": "Work Sans for all text",
        "images": "High-res product shots on cream background",
        "data_viz": "Matcha green (#406546) primary, gold (#C4A35A) accent",
    },
}


async def validate_content(content_type: str, content: dict) -> dict:
    """Validate content against brand guidelines.

    Returns a dict with 'valid' bool, 'issues' list, and 'suggestions' list.
    """
    issues = []
    suggestions = []

    template = CONTENT_TEMPLATES.get(content_type)
    if not template:
        return {"valid": False, "issues": [f"Unknown content type: {content_type}"], "suggestions": []}

    text = content.get("text", "")

    # Check for brand voice violations
    forbidden_phrases = [
        "buy now", "limited time only", "act fast", "don't miss out",
        "miracle", "cure", "guaranteed results", "#ad",
    ]
    for phrase in forbidden_phrases:
        if phrase.lower() in text.lower():
            issues.append(f"Brand voice violation: '{phrase}' — too aggressive/salesy")

    # Check hashtag count
    hashtag_count = text.count("#")
    max_hashtags = template.get("hashtags_max")
    if max_hashtags and hashtag_count > max_hashtags:
        issues.append(f"Too many hashtags: {hashtag_count} (max {max_hashtags})")

    # Check character limits
    max_chars = template.get("max_chars")
    if max_chars and len(text) > max_chars:
        issues.append(f"Text too long: {len(text)} chars (max {max_chars})")

    # Check word count for blog
    if content_type == "blog_article":
        word_count = len(text.split())
        min_words = template.get("min_words", 0)
        max_words = template.get("max_words", 99999)
        if word_count < min_words:
            issues.append(f"Blog too short: {word_count} words (min {min_words})")
        if word_count > max_words:
            suggestions.append(f"Blog may be too long: {word_count} words (target {max_words})")

    # Color check
    colors_used = content.get("colors", [])
    valid_colors = {c["hex"].lower() for c in BRAND_GUIDELINES["colors"].values()}
    for color in colors_used:
        if color.lower() not in valid_colors:
            issues.append(f"Off-brand color: {color} — not in brand palette")

    if not issues:
        suggestions.append("Content passes brand guidelines check")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def get_brand_guidelines() -> dict:
    """Return full brand guidelines."""
    return BRAND_GUIDELINES


def get_content_templates() -> dict:
    """Return all content templates."""
    return CONTENT_TEMPLATES


def get_template(content_type: str) -> dict:
    """Return template for a specific content type."""
    return CONTENT_TEMPLATES.get(content_type, {"error": f"Unknown type: {content_type}"})

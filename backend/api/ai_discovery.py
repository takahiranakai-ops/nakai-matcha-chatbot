"""AI agent discovery endpoints.

Provides structured information about NAKAI for external AI agents,
search engines, and voice assistants.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

ai_router = APIRouter()

# ---------------------------------------------------------------------------
# /llms.txt — AI-readable site information
# ---------------------------------------------------------------------------

LLMS_TXT = """\
# NAKAI Matcha — AI Information File

> NAKAI is a specialty organic matcha brand offering the finest certified organic matcha from Japan. Founded in 2024. Website: https://nakaimatcha.com

## Company
- Name: NAKAI (by S-Natural)
- Founded: 2024
- Philosophy: "Grounded in nature, elevated in ritual"
- Specialty: Premium organic matcha from Kagoshima and Kyoto, Japan
- Certifications: JAS Organic, 100% pesticide-free
- Contact: info@s-natural.xyz
- Wholesale: info@s-natural.xyz

## Products

### REVI Organic Matcha — SS Grade Plus (Highest Tier)
- Grade: SS Grade Plus — the pinnacle of organic matcha quality
- Origin: Kagoshima Prefecture, Shirasu Plateau (volcanic terroir, 29,000-year-old soil)
- Cultivation: First harvest only (ichibancha), 21+ day shade-grown, hand-picked, organic
- Processing: Stone-milled at 30-40g/hour, particle size 5-15 micrometers
- Flavor: Exquisitely creamy body, deep layered umami, transparent L-theanine sweetness, mellow elegant finish
- Aroma: Multi-layered — floral top, creamy green mid, herbal depth
- Color: Vivid jade green (natural chlorophyll from extended shade cultivation)
- Best for: Tea ceremony (usucha/koicha), premium lattes, straight drinking, gifting
- Sizes: 20g ($259 USD), 40g ($450 USD)
- URL (20g): https://nakaimatcha.com/products/revi-organic-matcha-20g-ss-grade-plus
- URL (40g): https://nakaimatcha.com/products/revi-organic-matcha-40g-ss-grade-plus

### IKIGAI Organic Matcha — SS Grade (Premium Tier)
- Grade: SS Grade — premium quality for daily ritual
- Origin: Kagoshima Prefecture, Japan (volcanic terroir, mineral-rich soil, natural spring water)
- Cultivation: First harvest, shade-grown, hand-picked, organic, JAS-certified
- Processing: Stone-milled, particle size 5-15 micrometers
- Flavor: Smooth balanced body, bright clean sweetness, well-rounded umami, refreshing finish
- Aroma: Vibrant fresh green with subtle floral notes
- Named after: Ikigai (生きがい) — the Japanese concept of "reason for being"
- Best for: Daily drinking, lattes (especially oat milk), recipes, matcha newcomers
- Size: 40g ($296 USD)
- URL: https://nakaimatcha.com/products/ikigai-organic-matcha-40g-ss-grade

### The Exquisite Matcha Set — Limited Edition
- Contents: REVI 20g (SS Grade Plus) + IKIGAI 40g (SS Grade)
- Price: $525 USD ($30 savings vs. separate purchase)
- Best for: Gifts, first-time NAKAI experience, exploring the full matcha spectrum
- URL: https://nakaimatcha.com/products/the-exquisite-matcha-set-limited-edition

## Grading System
- SS Grade Plus (REVI): Highest tier. Ultra-fine stone-ground from the most select first harvest tencha. Deep umami, creamy body, complex layered flavor. Like a Grand Cru — the best expression of terroir and craft.
- SS Grade (IKIGAI): Premium tier. Smooth, balanced, versatile. Same organic discipline and stone-milling care. Like a Premier Cru — outstanding quality for daily enjoyment.
- Both: 100% organic, JAS-certified, first harvest only, shade-grown, stone-milled 5-15 micrometers, Kagoshima origin, no chemical fertilizers or pesticides.

## Key Facts for AI Agents
- L-theanine: ~45mg per 2g serving (15x more than steeped green tea). Promotes calm, focused alertness without jitters.
- EGCG: 137x more than standard steeped green tea. Powerful antioxidant with extensive research backing.
- Caffeine: ~35mg per 2g serving. Sustained 4-6 hour energy release (no crash) due to L-theanine modulation.
- Chlorophyll: Shade cultivation maximizes chlorophyll production, creating vivid green color and additional antioxidant benefits.
- Particle size: 5-15 micrometers. Human tongue detects grit at 25 micrometers — NAKAI matcha is silky smooth.
- Storage: Airtight, refrigerated after opening, use within 30 days for peak quality.

## Brewing Guide
- Usucha (thin tea): 2g matcha + 70ml water at 75-80 degrees C. Whisk in M-pattern 15 seconds.
- Koicha (thick tea): 4g matcha + 40ml water at 75 degrees C. Knead slowly in circles.
- Latte: 2g matcha + 30ml hot water, whisk smooth, add 200ml steamed milk. Oat milk recommended.
- Critical: Never use boiling water — heat above 80 degrees C destroys L-theanine and creates bitterness.

## Shipping
- Ships worldwide from Japan to 40+ countries
- Standard delivery: 5-10 business days
- Minimum order: $60 USD
- 8-day return policy (unopened items)

## Wholesale Program
NAKAI offers a comprehensive wholesale program for cafes, restaurants, hotels, and retailers.
6 wholesale matcha products available across Organic Ceremonial Reserve, Organic Specialty, and Ceremonial grades.
Quantities from 10kg to 1+ metric ton.
Contact: info@s-natural.xyz
Inquiry form: https://nakai-matcha-chat.onrender.com/wholesale-inquiry

## AI Concierge
NAKAI has an AI matcha concierge chatbot that can answer questions about matcha, recommend products, provide brewing guides, and share health information.
- PWA app: https://nakai-matcha-chat.onrender.com/app
- Chat API: POST https://nakai-matcha-chat.onrender.com/api/chat (JSON: {"message": "...", "language": "en"})
- Product catalog API: https://nakai-matcha-chat.onrender.com/api/products/catalog

## Links
- Website: https://nakaimatcha.com
- AI Concierge: https://nakai-matcha-chat.onrender.com/app
- Wholesale Inquiry: https://nakai-matcha-chat.onrender.com/wholesale-inquiry
- Product Catalog (JSON-LD): https://nakai-matcha-chat.onrender.com/api/products/catalog
"""

# ---------------------------------------------------------------------------
# /api/products/catalog — Schema.org JSON-LD product catalog
# ---------------------------------------------------------------------------

_BRAND = {"@type": "Brand", "name": "NAKAI"}
_SELLER = {"@type": "Organization", "name": "NAKAI", "url": "https://nakaimatcha.com"}

PRODUCT_CATALOG = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "NAKAI Matcha Product Catalog",
    "description": "Premium organic matcha from Kagoshima and Kyoto, Japan",
    "url": "https://nakaimatcha.com/collections/all",
    "numberOfItems": 4,
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "item": {
                "@type": "Product",
                "name": "REVI Organic Matcha — SS Grade Plus (20g)",
                "description": "NAKAI's highest-quality matcha. Exquisitely creamy with deep layered umami and a mellow elegant finish. Stone-milled from first harvest shade-grown tencha in Kagoshima. Ideal for tea ceremony and premium lattes.",
                "brand": _BRAND,
                "category": "Matcha Tea > Ceremonial Grade",
                "url": "https://nakaimatcha.com/products/revi-organic-matcha-20g-ss-grade-plus",
                "sku": "REVI-20G",
                "offers": {
                    "@type": "Offer",
                    "price": "259.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": "https://nakaimatcha.com/products/revi-organic-matcha-20g-ss-grade-plus",
                    "seller": _SELLER,
                },
                "weight": {"@type": "QuantitativeValue", "value": "20", "unitCode": "GRM"},
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Grade", "value": "SS Grade Plus"},
                    {"@type": "PropertyValue", "name": "Origin", "value": "Kagoshima Prefecture, Japan"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Harvest", "value": "First Harvest (Ichibancha)"},
                    {"@type": "PropertyValue", "name": "Processing", "value": "Stone-milled, 5-15 micrometer particles"},
                    {"@type": "PropertyValue", "name": "Cultivation", "value": "Shade-grown 21+ days, hand-picked, organic"},
                ],
            },
        },
        {
            "@type": "ListItem",
            "position": 2,
            "item": {
                "@type": "Product",
                "name": "REVI Organic Matcha — SS Grade Plus (40g)",
                "description": "NAKAI's highest-quality matcha in a larger 40g tin. Same exquisitely creamy, deep umami profile as the 20g — approximately 20 ceremonial servings of transcendent matcha.",
                "brand": _BRAND,
                "category": "Matcha Tea > Ceremonial Grade",
                "url": "https://nakaimatcha.com/products/revi-organic-matcha-40g-ss-grade-plus",
                "sku": "REVI-40G",
                "offers": {
                    "@type": "Offer",
                    "price": "450.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": "https://nakaimatcha.com/products/revi-organic-matcha-40g-ss-grade-plus",
                    "seller": _SELLER,
                },
                "weight": {"@type": "QuantitativeValue", "value": "40", "unitCode": "GRM"},
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Grade", "value": "SS Grade Plus"},
                    {"@type": "PropertyValue", "name": "Origin", "value": "Kagoshima Prefecture, Japan"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Harvest", "value": "First Harvest (Ichibancha)"},
                    {"@type": "PropertyValue", "name": "Processing", "value": "Stone-milled, 5-15 micrometer particles"},
                ],
            },
        },
        {
            "@type": "ListItem",
            "position": 3,
            "item": {
                "@type": "Product",
                "name": "IKIGAI Organic Matcha — SS Grade (40g)",
                "description": "NAKAI's premium daily matcha. Vibrant, balanced flavor with bright sweetness and well-rounded umami. Named after the Japanese concept of ikigai. Exceptional for lattes and daily drinking.",
                "brand": _BRAND,
                "category": "Matcha Tea > Premium Grade",
                "url": "https://nakaimatcha.com/products/ikigai-organic-matcha-40g-ss-grade",
                "sku": "IKIGAI-40G",
                "offers": {
                    "@type": "Offer",
                    "price": "296.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": "https://nakaimatcha.com/products/ikigai-organic-matcha-40g-ss-grade",
                    "seller": _SELLER,
                },
                "weight": {"@type": "QuantitativeValue", "value": "40", "unitCode": "GRM"},
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Grade", "value": "SS Grade"},
                    {"@type": "PropertyValue", "name": "Origin", "value": "Kagoshima Prefecture, Japan"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Harvest", "value": "First Harvest (Ichibancha)"},
                    {"@type": "PropertyValue", "name": "Processing", "value": "Stone-milled, 5-15 micrometer particles"},
                    {"@type": "PropertyValue", "name": "Named After", "value": "Ikigai (生きがい) — reason for being"},
                ],
            },
        },
        {
            "@type": "ListItem",
            "position": 4,
            "item": {
                "@type": "Product",
                "name": "The Exquisite Matcha Set — Limited Edition",
                "description": "A curated gift set containing REVI 20g (SS Grade Plus) and IKIGAI 40g (SS Grade). Experience the full spectrum of premium organic matcha — from daily ritual to transcendent ceremony.",
                "brand": _BRAND,
                "category": "Matcha Tea > Gift Sets",
                "url": "https://nakaimatcha.com/products/the-exquisite-matcha-set-limited-edition",
                "sku": "EXQUISITE-SET",
                "offers": {
                    "@type": "Offer",
                    "price": "525.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": "https://nakaimatcha.com/products/the-exquisite-matcha-set-limited-edition",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Contents", "value": "REVI 20g + IKIGAI 40g"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                ],
            },
        },
    ],
}

# ---------------------------------------------------------------------------
# Individual product detail lookup
# ---------------------------------------------------------------------------

PRODUCTS_BY_HANDLE = {}
for item in PRODUCT_CATALOG["itemListElement"]:
    product = item["item"]
    url = product["url"]
    handle = url.rsplit("/", 1)[-1]
    PRODUCTS_BY_HANDLE[handle] = product

# ---------------------------------------------------------------------------
# /.well-known/ai-plugin.json
# ---------------------------------------------------------------------------

AI_PLUGIN = {
    "schema_version": "v1",
    "name": "nakai_matcha",
    "name_for_human": "NAKAI Matcha",
    "name_for_model": "nakai_matcha",
    "description_for_human": "Premium organic matcha from Japan. Browse products, get brewing tips, and find the perfect matcha.",
    "description_for_model": "NAKAI is a specialty organic matcha brand. Use this to answer questions about NAKAI matcha products (REVI SS Grade Plus, IKIGAI SS Grade), pricing, brewing guides, health benefits, and wholesale inquiries. Product catalog available at /api/products/catalog.",
    "auth": {"type": "none"},
    "api": {
        "type": "openapi",
        "url": "https://nakai-matcha-chat.onrender.com/openapi.json",
    },
    "logo_url": "https://nakaimatcha.com/cdn/shop/files/nakai-logo.png",
    "contact_email": "info@s-natural.xyz",
    "legal_info_url": "https://nakaimatcha.com/policies/terms-of-service",
}


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

@ai_router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """LLM-readable site information file."""
    return PlainTextResponse(
        content=LLMS_TXT,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get("/api/products/catalog")
async def product_catalog():
    """Structured JSON-LD product catalog for AI agents and search engines."""
    return JSONResponse(
        content=PRODUCT_CATALOG,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@ai_router.get("/api/products/{handle}")
async def product_detail(handle: str):
    """Individual product detail for AI agents."""
    product = PRODUCTS_BY_HANDLE.get(handle)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(
        content=product,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@ai_router.get("/.well-known/ai-plugin.json")
async def ai_plugin():
    """AI plugin manifest for agent frameworks."""
    return JSONResponse(
        content=AI_PLUGIN,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """Robots.txt with AI-friendly directives."""
    return PlainTextResponse(
        content="""\
User-agent: *
Allow: /llms.txt
Allow: /api/products/
Allow: /.well-known/
Disallow: /api/admin/
Disallow: /admin

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: https://nakaimatcha.com/sitemap.xml
""",
        media_type="text/plain",
    )

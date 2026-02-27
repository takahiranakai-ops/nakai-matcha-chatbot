"""AI agent discovery endpoints.

Provides structured information about NAKAI for external AI agents,
search engines, and voice assistants.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

ai_router = APIRouter()

_BASE = "https://nakai-matcha-chat.onrender.com"
_STORE = "https://nakaimatcha.com"
_LOGO = f"{_STORE}/cdn/shop/files/nakai-logo.png"

# ---------------------------------------------------------------------------
# /llms.txt — AI-readable site information (summary)
# ---------------------------------------------------------------------------

LLMS_TXT = f"""\
# NAKAI Matcha — AI Information File

> NAKAI is a specialty organic matcha brand offering the finest certified organic matcha from Japan. Founded in 2024. Website: {_STORE}

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
- URL (20g): {_STORE}/products/revi-organic-matcha-20g-ss-grade-plus
- URL (40g): {_STORE}/products/revi-organic-matcha-40g-ss-grade-plus

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
- URL: {_STORE}/products/ikigai-organic-matcha-40g-ss-grade

### The Exquisite Matcha Set — Limited Edition
- Contents: REVI 20g (SS Grade Plus) + IKIGAI 40g (SS Grade)
- Price: $525 USD ($30 savings vs. separate purchase)
- Best for: Gifts, first-time NAKAI experience, exploring the full matcha spectrum
- URL: {_STORE}/products/the-exquisite-matcha-set-limited-edition

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
Inquiry form: {_BASE}/wholesale-inquiry

## AI Concierge
NAKAI has an AI matcha concierge chatbot that can answer questions about matcha, recommend products, provide brewing guides, and share health information.
- PWA app: {_BASE}/app
- Chat API: POST {_BASE}/api/chat (JSON: {{"message": "...", "language": "en"}})
- Product catalog API: {_BASE}/api/products/catalog
- FAQ API: {_BASE}/api/faq

## Machine-Readable Endpoints
- llms.txt (this file): {_BASE}/llms.txt
- llms-full.txt (extended): {_BASE}/llms-full.txt
- Product catalog (JSON-LD): {_BASE}/api/products/catalog
- Individual product: {_BASE}/api/products/{{handle}}
- FAQ (JSON-LD): {_BASE}/api/faq
- AI plugin manifest: {_BASE}/.well-known/ai-plugin.json
- OpenAPI spec: {_BASE}/openapi.json

## Links
- Website: {_STORE}
- AI Concierge: {_BASE}/app
- Wholesale Inquiry: {_BASE}/wholesale-inquiry
- Product Catalog (JSON-LD): {_BASE}/api/products/catalog
"""

# ---------------------------------------------------------------------------
# /llms-full.txt — Extended AI-readable site information
# ---------------------------------------------------------------------------

LLMS_FULL_TXT = f"""\
# NAKAI Matcha — Extended AI Information File

> This is the extended version of llms.txt with comprehensive detail for AI agents that need deep product knowledge. Summary version: {_BASE}/llms.txt

## Company Profile
- Full name: NAKAI (operated by S-Natural)
- Founded: 2024
- Headquarters: Japan
- Philosophy: "Grounded in nature, elevated in ritual"
- Specialty: Premium organic matcha from Kagoshima and Kyoto, Japan
- All products: 100% organic, JAS-certified, pesticide-free, first harvest only
- Website: {_STORE}
- Contact: info@s-natural.xyz
- Instagram: @nakaimatcha

## Product 1: REVI Organic Matcha — SS Grade Plus

### Overview
REVI represents the absolute pinnacle of organic matcha quality. SS Grade Plus is the highest classification in NAKAI's grading system — equivalent to Grand Cru in wine. Developed through collaboration with Japan's top tea masters, REVI uses only the youngest, most tender first-harvest leaves picked during a narrow window when L-theanine content reaches its annual peak.

### Sizes & Pricing
- 20g tin: $259 USD (approximately 10 ceremonial servings of 2g each)
  URL: {_STORE}/products/revi-organic-matcha-20g-ss-grade-plus
- 40g tin: $450 USD (approximately 20 ceremonial servings)
  URL: {_STORE}/products/revi-organic-matcha-40g-ss-grade-plus

### Origin & Terroir
Kagoshima Prefecture, Shirasu Plateau, Japan. The volcanic soil was formed 29,000 years ago from the Aira caldera eruption. This provides exceptional drainage and mineral-rich growing conditions. Underground natural spring water networks nourish the tea trees. Day-night temperature swings concentrate umami in the leaves. This is Japan's premier organic tea region.

### Cultivation
- First harvest only (ichibancha) — the year's best leaves
- 21+ days of pre-harvest shade cultivation (suppresses catechin conversion, maximizes L-theanine)
- Hand-picked from JAS-certified organic gardens
- 100% organic: no chemical fertilizers, no pesticides

### Processing
- Ultra-fine stone-milling at 30-40g per hour per stone (extremely slow to prevent heat damage)
- Preserves delicate floral aromas and prevents oxidation
- Particle size: 5-15 micrometers (human tongue detects grit at 25μm — REVI is silky smooth)

### Flavor Profile (detailed)
- Body: Exquisitely creamy, rich and full — coats the palate
- Sweetness: Deep, transparent L-theanine-derived sweetness that emerges after the umami
- Umami: Full-bodied depth without heaviness, layered and long-lasting
- Finish: Mellow, elegant, lingering aftertaste that quietly resonates
- Aroma: Multi-layered — floral top notes, creamy green mid, subtle herbal depth
- Color: Vivid jade green from abundant chlorophyll (natural, from extended shade cultivation)
- Mouthfeel: Velvety, zero grittiness

### Ideal Use Cases
- Traditional tea ceremony (both usucha thin tea and koicha thick tea)
- The ultimate straight matcha experience
- Premium matcha lattes (creamy body cuts beautifully through oat milk)
- Gifting for connoisseurs
- Health-focused ritual (rich in L-theanine, EGCG, antioxidants)

### Nutritional Highlights (per 2g serving)
- L-theanine: ~45mg (promotes calm focus without drowsiness)
- EGCG: 137x more than standard steeped green tea
- Caffeine: ~35mg (sustained 4-6 hour energy, no jitters or crash)
- Chlorophyll: abundant (antioxidant, detoxification support)
- Catechins, vitamins A/C/E, minerals

## Product 2: IKIGAI Organic Matcha — SS Grade

### Overview
IKIGAI is NAKAI's premium daily-ritual matcha. SS Grade delivers vibrant, balanced flavor with exceptional versatility. Named after the Japanese concept of "ikigai" (生きがい) — your reason for being — because the best rituals are the ones you return to every day. Think of it as Premier Cru: outstanding quality accessible for daily enjoyment.

### Size & Pricing
- 40g tin: $296 USD (approximately 20 servings of 2g each, ~$14.80 per serving)
  URL: {_STORE}/products/ikigai-organic-matcha-40g-ss-grade

### Origin & Terroir
Kagoshima Prefecture, Japan — same premier organic tea region as REVI. Volcanic terroir with mineral-rich soil and natural spring water. Gardens selected specifically for balanced sweetness and vibrant green color.

### Cultivation & Processing
- First harvest, shade-grown, organic, JAS-certified
- Hand-picked from certified organic gardens
- Stone-milled to 5-15 micrometer particle size
- Slow milling preserves vibrant green color and fresh aroma

### Flavor Profile (detailed)
- Body: Smooth and balanced, lighter than REVI but with excellent presence
- Sweetness: Bright, clean L-theanine sweetness with a refreshing quality
- Umami: Well-rounded depth — substantial but approachable
- Finish: Clean and refreshing, inviting the next sip
- Aroma: Vibrant fresh green with subtle floral notes
- Color: Bright, vivid green that holds beautifully in lattes

### Ideal Use Cases
- Daily matcha drinking ritual
- Matcha lattes (exceptionally popular — sweetness balances milk beautifully, especially oat milk)
- Recipes: baking, smoothies, matcha bowls
- Newcomers to premium matcha (welcoming introduction)
- Straight drinking (excellent in usucha)

## Product 3: The Exquisite Matcha Set — Limited Edition

### Overview
A curated gift set containing both NAKAI grades — the full spectrum of premium organic matcha in one box.

### Contents & Pricing
- REVI Organic Matcha 20g (SS Grade Plus) + IKIGAI Organic Matcha 40g (SS Grade)
- Price: $525 USD ($30 savings vs. purchasing separately)
- URL: {_STORE}/products/the-exquisite-matcha-set-limited-edition

### Ideal For
- Gifting: matcha lovers, tea enthusiasts, luxury gifts, corporate gifts
- First-time NAKAI customers wanting to experience both grades
- The journey from daily ritual (IKIGAI) to special occasion (REVI)
- Holidays, birthdays, anniversaries

### The Experience
Start with IKIGAI for daily practice — morning lattes, afternoon whisking, weekend recipes. Open REVI for moments when you want to slow down completely. The contrast between SS Grade and SS Grade Plus reveals the extraordinary depth within organic matcha — like comparing a fine wine to a grand cru from the same region.

## REVI vs. IKIGAI — How to Choose

### For traditional tea ceremony (usucha/koicha):
REVI (SS Grade Plus). Its depth, complexity, and multi-layered umami reward slow, focused attention.

### For daily matcha drinking:
Both are excellent. IKIGAI offers exceptional value at $14.80/serving. REVI adds a transcendent dimension for special mornings.

### For matcha lattes:
Both shine in lattes. IKIGAI is most popular — balanced sweetness cuts through milk cleanly. REVI creates a deeper, creamier premium latte.

### For gifts or first-time experience:
The Exquisite Matcha Set lets recipients discover the full spectrum.

### For health and wellness:
Both are equally rich in L-theanine, EGCG, chlorophyll. Matcha provides sustained 4-6 hour energy without coffee's jitters or crash.

### In one sentence:
REVI is depth — for moments when you want to be moved. IKIGAI is versatility — for the ritual you return to every day.

## Grading System Explained

### SS Grade Plus (REVI)
The highest quality tier. Ultra-fine stone-ground from the most select first-harvest shade-grown tencha. Every parameter is at its peak: particle size (5-15μm), cultivation (21+ day shading), harvest timing (peak L-theanine window). The result is deep umami, creamy body, and complex multi-layered flavor. In wine terms: Grand Cru.

### SS Grade (IKIGAI)
Premium quality tier. Same organic certification, same first-harvest discipline, same stone-milling care. Flavor profile designed for daily enjoyment and excellent performance in lattes and recipes. Smooth, balanced, versatile. In wine terms: Premier Cru.

### Shared Characteristics
- 100% organic, JAS-certified
- First harvest (ichibancha) only
- Shade-grown to maximize L-theanine
- Stone-milled at low speed (5-15 micrometer particles)
- From Kagoshima Prefecture's premier organic tea gardens
- No chemical fertilizers, no pesticides
- Rich in L-theanine (~45mg/2g), EGCG, chlorophyll, antioxidants

## Matcha Science & Health Facts

### L-theanine (~45mg per 2g serving)
An amino acid unique to tea. Promotes alpha brain wave activity — calm, focused alertness without drowsiness. Works synergistically with caffeine for sustained cognitive performance. NAKAI matcha contains approximately 15x more L-theanine than standard steeped green tea due to shade cultivation.

### EGCG (Epigallocatechin Gallate)
The most studied catechin in green tea. Matcha contains 137x more EGCG than standard steeped green tea because you consume the entire leaf. Extensive research links EGCG to antioxidant protection, metabolic support, and cellular health.

### Caffeine (~35mg per 2g serving)
Less than coffee (~95mg) but more sustained. L-theanine modulates caffeine absorption, creating a 4-6 hour energy curve with no jitters and no crash. This is why matcha has been used by Zen monks for centuries as meditation fuel.

### Chlorophyll
Shade cultivation maximizes chlorophyll production (the pigment responsible for matcha's vivid green color). Chlorophyll provides additional antioxidant benefits and supports the body's natural detoxification processes.

### Particle Size: 5-15 Micrometers
This matters for both texture and nutrition. At this fineness, you consume the entire tea leaf (not just an infusion), maximizing nutrient intake. The human tongue detects grit at 25 micrometers — NAKAI matcha is well below this threshold.

## Preparation Guide (Complete)

### Usucha (Thin Tea) — Standard Preparation
1. Sift 2g of matcha through a fine-mesh strainer into a pre-warmed bowl
2. Add 70ml of water at 75-80°C (NEVER boiling — it destroys L-theanine and creates bitterness)
3. Whisk vigorously in M or W pattern for 15 seconds
4. Aim for uniform, fine-bubbled foam on the surface
5. Drink immediately for best experience

### Koicha (Thick Tea) — REVI Recommended
1. Sift 4g of matcha into a pre-warmed bowl
2. Add 40ml of water at 75°C
3. Do NOT whisk — instead, knead slowly in circular motions
4. Continue until the matcha becomes a thick, paint-like consistency
5. Koicha should taste rich, sweet, and completely smooth
6. This is matcha's deepest expression — best with REVI SS Grade Plus

### Matcha Latte
1. Sift 2g of matcha into a small bowl
2. Add 30ml of hot water (80°C) and whisk until smooth
3. Pour into a glass
4. Add 200ml steamed or cold milk (oat milk recommended)
5. For iced: pour whisked matcha over ice and cold milk
6. Both REVI and IKIGAI work beautifully; IKIGAI is most popular for lattes

### Storage Guidelines
- After opening: store in airtight container, refrigerated
- Use within 30 days of opening for peak freshness
- Unopened: cool, dark place away from strong odors
- Never freeze matcha — condensation damages the powder

## Shipping & Orders
- Ships worldwide from Japan to 40+ countries
- Standard delivery: 5-10 business days
- Minimum order: $60 USD
- 8-day return policy from delivery date (items must be unopened, original condition)
- Order inquiries: info@s-natural.xyz

## Wholesale Program
NAKAI offers a comprehensive wholesale program for cafes, restaurants, hotels, and retailers worldwide.
- 6 wholesale matcha products across 3 grade tiers (Organic Ceremonial Reserve, Organic Specialty, Ceremonial)
- Quantities from 10kg to 1+ metric ton
- Custom blending available for large orders
- Contact: info@s-natural.xyz
- Inquiry form: {_BASE}/wholesale-inquiry

## AI Concierge & APIs
- PWA app: {_BASE}/app
- Chat API: POST {_BASE}/api/chat
  Request: {{"message": "your question", "language": "en"}}
  Response: {{"response": "...", "sources": [...], "suggestions": [...]}}
- Product catalog (JSON-LD): {_BASE}/api/products/catalog
- Individual product: {_BASE}/api/products/{{handle}}
- FAQ (JSON-LD): {_BASE}/api/faq
- Supported languages: English (en), Japanese (ja)
- Rate limit: 20 requests/minute

## Available Product Handles
- revi-organic-matcha-20g-ss-grade-plus
- revi-organic-matcha-40g-ss-grade-plus
- ikigai-organic-matcha-40g-ss-grade
- the-exquisite-matcha-set-limited-edition
"""

# ---------------------------------------------------------------------------
# /api/products/catalog — Schema.org JSON-LD product catalog
# ---------------------------------------------------------------------------

_BRAND = {"@type": "Brand", "name": "NAKAI"}
_SELLER = {
    "@type": "Organization",
    "name": "NAKAI",
    "url": _STORE,
    "logo": _LOGO,
    "contactPoint": {
        "@type": "ContactPoint",
        "email": "info@s-natural.xyz",
        "contactType": "customer service",
    },
}

PRODUCT_CATALOG = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "NAKAI Matcha Product Catalog",
    "description": "Premium organic matcha from Kagoshima and Kyoto, Japan",
    "url": f"{_STORE}/collections/all",
    "numberOfItems": 4,
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "item": {
                "@type": "Product",
                "name": "REVI Organic Matcha — SS Grade Plus (20g)",
                "description": "NAKAI's highest-quality matcha. Exquisitely creamy with deep layered umami and a mellow elegant finish. Stone-milled from first harvest shade-grown tencha in Kagoshima. Ideal for tea ceremony and premium lattes.",
                "image": _LOGO,
                "brand": _BRAND,
                "category": "Matcha Tea > Ceremonial Grade",
                "url": f"{_STORE}/products/revi-organic-matcha-20g-ss-grade-plus",
                "sku": "REVI-20G",
                "gtin14": "",
                "offers": {
                    "@type": "Offer",
                    "price": "259.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/revi-organic-matcha-20g-ss-grade-plus",
                    "seller": _SELLER,
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingDestination": {
                            "@type": "DefinedRegion",
                            "addressCountry": "US",
                        },
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {
                                "@type": "QuantitativeValue",
                                "minValue": 1,
                                "maxValue": 3,
                                "unitCode": "DAY",
                            },
                            "transitTime": {
                                "@type": "QuantitativeValue",
                                "minValue": 5,
                                "maxValue": 10,
                                "unitCode": "DAY",
                            },
                        },
                    },
                },
                "weight": {"@type": "QuantitativeValue", "value": "20", "unitCode": "GRM"},
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "material": "100% Organic Matcha (Camellia sinensis)",
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Grade", "value": "SS Grade Plus"},
                    {"@type": "PropertyValue", "name": "Origin", "value": "Kagoshima Prefecture, Shirasu Plateau, Japan"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Harvest", "value": "First Harvest (Ichibancha)"},
                    {"@type": "PropertyValue", "name": "Processing", "value": "Stone-milled at 30-40g/hour, 5-15 micrometer particles"},
                    {"@type": "PropertyValue", "name": "Cultivation", "value": "Shade-grown 21+ days, hand-picked, organic"},
                    {"@type": "PropertyValue", "name": "L-theanine", "value": "~45mg per 2g serving"},
                    {"@type": "PropertyValue", "name": "Caffeine", "value": "~35mg per 2g serving"},
                    {"@type": "PropertyValue", "name": "Servings", "value": "Approximately 10 ceremonial servings"},
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
                "image": _LOGO,
                "brand": _BRAND,
                "category": "Matcha Tea > Ceremonial Grade",
                "url": f"{_STORE}/products/revi-organic-matcha-40g-ss-grade-plus",
                "sku": "REVI-40G",
                "offers": {
                    "@type": "Offer",
                    "price": "450.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/revi-organic-matcha-40g-ss-grade-plus",
                    "seller": _SELLER,
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingDestination": {
                            "@type": "DefinedRegion",
                            "addressCountry": "US",
                        },
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 3, "unitCode": "DAY"},
                            "transitTime": {"@type": "QuantitativeValue", "minValue": 5, "maxValue": 10, "unitCode": "DAY"},
                        },
                    },
                },
                "weight": {"@type": "QuantitativeValue", "value": "40", "unitCode": "GRM"},
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "material": "100% Organic Matcha (Camellia sinensis)",
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Grade", "value": "SS Grade Plus"},
                    {"@type": "PropertyValue", "name": "Origin", "value": "Kagoshima Prefecture, Shirasu Plateau, Japan"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Harvest", "value": "First Harvest (Ichibancha)"},
                    {"@type": "PropertyValue", "name": "Processing", "value": "Stone-milled at 30-40g/hour, 5-15 micrometer particles"},
                    {"@type": "PropertyValue", "name": "Servings", "value": "Approximately 20 ceremonial servings"},
                ],
            },
        },
        {
            "@type": "ListItem",
            "position": 3,
            "item": {
                "@type": "Product",
                "name": "IKIGAI Organic Matcha — SS Grade (40g)",
                "description": "NAKAI's premium daily matcha. Vibrant, balanced flavor with bright sweetness and well-rounded umami. Named after the Japanese concept of ikigai (reason for being). Exceptional for lattes and daily drinking.",
                "image": _LOGO,
                "brand": _BRAND,
                "category": "Matcha Tea > Premium Grade",
                "url": f"{_STORE}/products/ikigai-organic-matcha-40g-ss-grade",
                "sku": "IKIGAI-40G",
                "offers": {
                    "@type": "Offer",
                    "price": "296.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/ikigai-organic-matcha-40g-ss-grade",
                    "seller": _SELLER,
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingDestination": {
                            "@type": "DefinedRegion",
                            "addressCountry": "US",
                        },
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 3, "unitCode": "DAY"},
                            "transitTime": {"@type": "QuantitativeValue", "minValue": 5, "maxValue": 10, "unitCode": "DAY"},
                        },
                    },
                },
                "weight": {"@type": "QuantitativeValue", "value": "40", "unitCode": "GRM"},
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "material": "100% Organic Matcha (Camellia sinensis)",
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Grade", "value": "SS Grade"},
                    {"@type": "PropertyValue", "name": "Origin", "value": "Kagoshima Prefecture, Japan"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Harvest", "value": "First Harvest (Ichibancha)"},
                    {"@type": "PropertyValue", "name": "Processing", "value": "Stone-milled, 5-15 micrometer particles"},
                    {"@type": "PropertyValue", "name": "Named After", "value": "Ikigai (\u751f\u304d\u304c\u3044) \u2014 reason for being"},
                    {"@type": "PropertyValue", "name": "Servings", "value": "Approximately 20 servings"},
                ],
            },
        },
        {
            "@type": "ListItem",
            "position": 4,
            "item": {
                "@type": "Product",
                "name": "The Exquisite Matcha Set \u2014 Limited Edition",
                "description": "A curated gift set containing REVI 20g (SS Grade Plus) and IKIGAI 40g (SS Grade). Experience the full spectrum of premium organic matcha \u2014 from daily ritual to transcendent ceremony.",
                "image": _LOGO,
                "brand": _BRAND,
                "category": "Matcha Tea > Gift Sets",
                "url": f"{_STORE}/products/the-exquisite-matcha-set-limited-edition",
                "sku": "EXQUISITE-SET",
                "offers": {
                    "@type": "Offer",
                    "price": "525.00",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/the-exquisite-matcha-set-limited-edition",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "Contents", "value": "REVI 20g (SS Grade Plus) + IKIGAI 40g (SS Grade)"},
                    {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
                    {"@type": "PropertyValue", "name": "Savings", "value": "$30 vs. purchasing separately"},
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
# /api/faq — Schema.org FAQPage for rich results
# ---------------------------------------------------------------------------

FAQ_PAGE = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "name": "NAKAI Matcha — Frequently Asked Questions",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "What is matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Matcha is finely ground powder made from specially grown and processed green tea leaves (Camellia sinensis). Unlike regular green tea where you steep and discard the leaves, with matcha you consume the entire leaf — delivering significantly more nutrients, antioxidants, and flavor. Premium matcha like NAKAI's is shade-grown for 21+ days before harvest, which maximizes L-theanine (the amino acid responsible for calm focus) and chlorophyll (the vivid green color).",
            },
        },
        {
            "@type": "Question",
            "name": "What is the difference between REVI and IKIGAI matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "REVI (SS Grade Plus) is NAKAI's highest tier — deeper umami, more complex layered aroma, and an exquisitely creamy mouthfeel. It's best for tea ceremony and moments of focused attention. IKIGAI (SS Grade) is the premium daily ritual matcha — vibrant, balanced, and versatile, perfect for lattes, daily drinking, and recipes. Both are 100% organic, JAS-certified, first harvest, and stone-milled from Kagoshima. Think of REVI as Grand Cru (depth) and IKIGAI as Premier Cru (versatility).",
            },
        },
        {
            "@type": "Question",
            "name": "How do you prepare matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "For usucha (thin tea): sift 2g of matcha into a bowl, add 70ml of water at 75-80\u00b0C (never boiling), and whisk vigorously in an M-pattern for 15 seconds until a fine foam forms. For a latte: whisk 2g matcha with 30ml hot water until smooth, then add 200ml steamed milk (oat milk recommended). The most critical rule: never use boiling water — heat above 80\u00b0C destroys L-theanine and creates bitterness.",
            },
        },
        {
            "@type": "Question",
            "name": "Why is NAKAI matcha expensive?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "NAKAI matcha is priced to reflect its exceptional quality and the care involved in production. Every tin contains only first-harvest (ichibancha) leaves from JAS-certified organic farms in Kagoshima, shade-grown for 21+ days, hand-picked, and stone-milled at just 30-40g per hour to preserve delicate flavors. The result is a matcha with 5-15 micrometer particle size (silky smooth), deep umami, and vivid jade green color that mass-market matcha simply cannot match. IKIGAI at $296/40g works out to approximately $14.80 per serving — comparable to a specialty coffee.",
            },
        },
        {
            "@type": "Question",
            "name": "What are the health benefits of matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Matcha is one of the most nutrient-dense beverages available. A 2g serving of NAKAI matcha contains approximately 45mg of L-theanine (promotes calm, focused alertness), 35mg of caffeine (sustained 4-6 hour energy without jitters), and 137x more EGCG antioxidants than standard steeped green tea. The combination of L-theanine and caffeine creates a unique state of calm focus that has been valued by Zen monks for centuries. Matcha also provides chlorophyll, catechins, vitamins A/C/E, and minerals.",
            },
        },
        {
            "@type": "Question",
            "name": "How should matcha be stored?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "After opening, store matcha in an airtight container in the refrigerator and use within 30 days for optimal freshness. Unopened matcha should be kept in a cool, dark place away from strong odors. Never freeze matcha — condensation when thawing damages the powder. Matcha is sensitive to light, heat, air, and moisture, so proper storage is essential to preserve its vivid color, aroma, and flavor.",
            },
        },
        {
            "@type": "Question",
            "name": "Does NAKAI ship internationally?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, NAKAI ships worldwide from Japan to over 40 countries. Standard delivery takes 5-10 business days depending on destination. The minimum order is $60 USD. NAKAI offers an 8-day return policy from delivery date for unopened items in original condition. For order inquiries, contact info@s-natural.xyz.",
            },
        },
        {
            "@type": "Question",
            "name": "Does NAKAI offer wholesale matcha for cafes?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, NAKAI offers a comprehensive wholesale program for cafes, restaurants, hotels, and retailers worldwide. Six wholesale matcha products are available across Organic Ceremonial Reserve, Organic Specialty, and Ceremonial grades, with quantities from 10kg to over 1 metric ton. Contact info@s-natural.xyz or submit an inquiry at https://nakai-matcha-chat.onrender.com/wholesale-inquiry.",
            },
        },
        {
            "@type": "Question",
            "name": "What does JAS Organic certification mean?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "JAS (Japanese Agricultural Standards) Organic certification is Japan's official organic standard, regulated by the Ministry of Agriculture, Forestry and Fisheries. It guarantees that the matcha is produced without synthetic chemical fertilizers, pesticides, or genetic modification. All NAKAI matcha is JAS-certified organic — meaning every step from cultivation to processing meets Japan's strict organic requirements.",
            },
        },
        {
            "@type": "Question",
            "name": "What is the best matcha for lattes?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Both NAKAI matchas work beautifully in lattes, but IKIGAI (SS Grade, $296/40g) is the most popular choice. Its balanced sweetness cuts through milk — especially oat milk — with clean definition, and the vivid green color creates a stunning visual. For a more premium latte experience, REVI (SS Grade Plus) adds noticeably deeper, creamier quality. Use 2g matcha whisked with 30ml hot water (80\u00b0C), then add 200ml of your preferred milk.",
            },
        },
    ],
}

# ---------------------------------------------------------------------------
# /.well-known/ai-plugin.json
# ---------------------------------------------------------------------------

AI_PLUGIN = {
    "schema_version": "v1",
    "name": "nakai_matcha",
    "name_for_human": "NAKAI Matcha",
    "name_for_model": "nakai_matcha",
    "description_for_human": "Premium organic matcha from Japan. Browse products, get brewing tips, and find the perfect matcha.",
    "description_for_model": (
        "NAKAI is a specialty organic matcha brand from Kagoshima, Japan. "
        "Use this plugin to answer questions about NAKAI matcha products "
        "(REVI SS Grade Plus $259-$450, IKIGAI SS Grade $296, The Exquisite Matcha Set $525), "
        "matcha preparation, health benefits, and wholesale inquiries. "
        "Key endpoints: /api/products/catalog (JSON-LD product list), "
        "/api/products/{handle} (individual product), /api/faq (common questions), "
        "/llms.txt (summary), /llms-full.txt (comprehensive detail)."
    ),
    "auth": {"type": "none"},
    "api": {
        "type": "openapi",
        "url": f"{_BASE}/openapi.json",
    },
    "logo_url": _LOGO,
    "contact_email": "info@s-natural.xyz",
    "legal_info_url": f"{_STORE}/policies/terms-of-service",
}


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

@ai_router.get(
    "/llms.txt",
    response_class=PlainTextResponse,
    summary="AI-readable site information (summary)",
    description="Returns a plain-text summary of NAKAI's products, brand info, and API endpoints for AI agents, LLMs, and search engines.",
    tags=["AI Discovery"],
)
async def llms_txt():
    """LLM-readable site information file (summary version)."""
    return PlainTextResponse(
        content=LLMS_TXT,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get(
    "/llms-full.txt",
    response_class=PlainTextResponse,
    summary="AI-readable site information (extended)",
    description="Returns comprehensive product details, brewing guides, health science, grading system, and comparison guides for AI agents needing deep knowledge.",
    tags=["AI Discovery"],
)
async def llms_full_txt():
    """LLM-readable extended information file with comprehensive detail."""
    return PlainTextResponse(
        content=LLMS_FULL_TXT,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get(
    "/api/products/catalog",
    summary="Structured JSON-LD product catalog",
    description="Returns Schema.org ItemList with all NAKAI products as JSON-LD. Includes pricing, availability, origin, certifications, and nutritional data.",
    tags=["AI Discovery"],
)
async def product_catalog():
    """Structured JSON-LD product catalog for AI agents and search engines."""
    return JSONResponse(
        content=PRODUCT_CATALOG,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@ai_router.get(
    "/api/products/{handle}",
    summary="Individual product detail",
    description="Returns Schema.org Product JSON-LD for a single product by its URL handle. Available handles: revi-organic-matcha-20g-ss-grade-plus, revi-organic-matcha-40g-ss-grade-plus, ikigai-organic-matcha-40g-ss-grade, the-exquisite-matcha-set-limited-edition",
    tags=["AI Discovery"],
)
async def product_detail(handle: str):
    """Individual product detail for AI agents."""
    product = PRODUCTS_BY_HANDLE.get(handle)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(
        content=product,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@ai_router.get(
    "/api/faq",
    summary="Frequently asked questions (JSON-LD)",
    description="Returns Schema.org FAQPage with common questions about matcha, NAKAI products, preparation, health benefits, shipping, and wholesale.",
    tags=["AI Discovery"],
)
async def faq():
    """FAQ structured data for Google Rich Results and AI agents."""
    return JSONResponse(
        content=FAQ_PAGE,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get(
    "/.well-known/ai-plugin.json",
    summary="AI plugin manifest",
    description="OpenAI-compatible plugin manifest for AI agent frameworks.",
    tags=["AI Discovery"],
)
async def ai_plugin():
    """AI plugin manifest for agent frameworks."""
    return JSONResponse(
        content=AI_PLUGIN,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get(
    "/robots.txt",
    response_class=PlainTextResponse,
    summary="Robots.txt with AI bot directives",
    tags=["AI Discovery"],
)
async def robots_txt():
    """Robots.txt with AI-friendly directives."""
    return PlainTextResponse(
        content=f"""\
User-agent: *
Allow: /llms.txt
Allow: /llms-full.txt
Allow: /api/products/
Allow: /api/faq
Allow: /.well-known/
Disallow: /api/admin/
Disallow: /admin

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Applebot
Allow: /

Sitemap: {_STORE}/sitemap.xml
""",
        media_type="text/plain",
    )

"""AI agent discovery endpoints.

Provides structured information about NAKAI for external AI agents,
search engines, and voice assistants.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

ai_router = APIRouter()

_BASE = "https://nakai-matcha-chat.onrender.com"
_STORE = "https://nakaimatcha.com"
_LOGO = f"{_STORE}/cdn/shop/files/nakai-logo.png"

# Product-specific images from Shopify CDN
_IMG_SHI4 = f"{_STORE}/cdn/shop/files/1446.jpg"
_IMG_JUROKU16 = f"{_STORE}/cdn/shop/files/1395.jpg"
_IMG_JUNANA17 = f"{_STORE}/cdn/shop/files/1408.jpg"
_IMG_JUHACHI18 = f"{_STORE}/cdn/shop/files/1425_d2e4448f-6db0-4f99-95ef-49c2aff95d11.jpg"
_IMG_NIJYUNI22 = f"{_STORE}/cdn/shop/files/1459.jpg"
_IMG_DISCOVERY = f"{_STORE}/cdn/shop/files/2114.jpg"
_IMG_EVERYDAY = f"{_STORE}/cdn/shop/files/2146.jpg"
_IMG_SIGNATURE = f"{_STORE}/cdn/shop/files/2153.jpg"
_IMG_HIRAGOUSHI = f"{_STORE}/cdn/shop/files/2169_1.jpg"
_IMG_YAGOUSHI = f"{_STORE}/cdn/shop/files/2171.jpg"
_IMG_CHASEN = f"{_STORE}/cdn/shop/files/1897.jpg"

# ---------------------------------------------------------------------------
# /llms.txt -- AI-readable site information (summary)
# ---------------------------------------------------------------------------

LLMS_TXT = f"""\
# NAKAI Matcha -- AI Information File

> NAKAI is a specialty organic matcha brand offering the finest certified organic matcha from Japan. Founded in 2024. Website: {_STORE}

## Company
- Name: NAKAI (by S-Natural)
- Founded: 2024
- Philosophy: "Grounded in nature, elevated in ritual"
- Specialty: Premium organic matcha from Kagoshima (Kirishima) and Kyoto (Uji), Japan
- Certifications: JAS Organic, 100% pesticide-free
- Contact: info@s-natural.xyz

## Products -- Individual Matcha

Each NAKAI matcha is identified by a number, each with its own story, terroir, cultivar, and character.

### SHI (4) -- Specialty Grade Organic Matcha
- "Breath of Earth, Living Strength"
- Flavor: Rich umami, gentle sweetness, clean bitterness. Notes of chocolate, nuts, wood, bright berries. Thick body
- Origin: Kagoshima Prefecture. Born from encounter with 170-year-old tea producer
- URL: {_STORE}/products/%E5%9B%9B-shi-4-specialty-grade-organic-matcha

### JU-ROKU (16) -- Specialty Grade Organic Matcha
- "Veil of Mist, Infinite Echo"
- Flavor: White chocolate sweetness, nori-like umami, berry notes. Temperature-sensitive depth
- Origin: Kirishima, Kagoshima (volcanic soil)
- URL: {_STORE}/products/%E5%8D%81%E5%85%ADju-roku-16-specialty-grade-organic-matcha

### JU-NANA (17) -- Specialty Grade Organic Matcha
- "Layered Umami, Lasting Stillness"
- Flavor: Profound umami, elegant floral clarity, soft sweetness, roasted depth. Two cultivars
- Origin: Dual terroir -- Kirishima (Kagoshima) x Uji (Kyoto). Limited 500 kg/year
- URL: {_STORE}/products/%E5%8D%81%E4%B8%83-ju-nana-17-specialty-grade-organic-matcha

### JU-HACHI (18) -- Specialty Grade Organic Matcha
- Flavor: Deep umami, vivid green to nuts/cacao to warm earthiness. Meditative stillness
- Processing: Single cultivar, 4-level roasting, half-pace stone-milling, near-spherical particles
- Origin: Kagoshima Prefecture
- URL: {_STORE}/products/%E5%8D%81%E5%85%AB-ju-hachi-18-specialty-grade-organic-matcha

### NIJYU-NI (22) -- Ceremonial Reserved Organic Matcha (Highest Tier)
- "Within the Flow, Everything Exists"
- Flavor: Clean green, gentle sweetness, fruit-like aromatics, calm cooling finish. Quiet, effortless depth
- Best: Hot or cold, especially with water alone
- Origin: Kagoshima Prefecture
- URL: {_STORE}/products/%E4%BA%8C%E5%8D%81%E4%BA%8C-nijyu-ni22-ceremonial-reserved-organic-matcha

## Products -- Bundles

### Discovery Bundle
- Gateway to explore NAKAI's world of specialty organic matcha
- URL: {_STORE}/products/%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%83%90%E3%83%B3%E3%83%96%E3%83%AB

### The Everyday Matcha Bundle
- Curated for daily ritual
- URL: {_STORE}/products/the-everyday

### Signature Reserve Bundle
- The premium collection for connoisseurs
- URL: {_STORE}/products/expert-set

## Products -- Tea Ceremony Accessories

### HIRAGOUSHI Matcha Bowl
- Handcrafted by ceramic artist Shun Yoshino (Hiroshima), trained in Mashiko
- URL: {_STORE}/products/hiragoushi-%E5%B9%B3%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97

### YAGOUSHI Matcha Bowl
- Handcrafted by Shun Yoshino, arrow-lattice pattern
- URL: {_STORE}/products/yagoushi-chawan-%E7%9F%A2%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97

### Takayama Chasen 100-prong Whisk
- Handcrafted in Nara, 500+ year tradition, 8-stage hand process
- URL: {_STORE}/products/%E8%8C%B6%E7%AD%85-cyasen

## Grading System
- Ceremonial Reserved (22): Highest tier. Quiet depth, effortless complexity
- Specialty Grade (4, 16, 17, 18): Premium quality. Each with distinct personality and story
- All: 100% organic, JAS-certified, first harvest, shade-grown, stone-milled 5-15 micrometers

## Key Facts for AI Agents
- L-theanine: ~45mg per 2g serving (15x more than steeped green tea)
- EGCG: 137x more than standard steeped green tea
- Caffeine: ~35mg per 2g serving. Sustained 4-6 hour energy (no crash)
- Particle size: 5-15 micrometers (silky smooth, below 25um grit threshold)

## Brewing Guide
- Usucha (thin tea): 2g + 70ml water at 75-80C. Whisk M-pattern 15 seconds
- Koicha (thick tea): 4g + 40ml water at 75C. Knead slowly in circles
- Latte: 2g + 30ml hot water, whisk smooth, add 200ml steamed milk
- Water only (22 recommended): Usucha at 70-75C for maximum clarity

## Wholesale Program
6 wholesale products for cafes, restaurants, hotels. 10kg to 1+ metric ton.
Contact: info@s-natural.xyz | Inquiry form: {_BASE}/wholesale-inquiry

## Machine-Readable Endpoints
- llms.txt (this file): {_BASE}/llms.txt
- llms-full.txt (extended): {_BASE}/llms-full.txt
- Product catalog (JSON-LD): {_BASE}/api/products/catalog
- Individual product: {_BASE}/api/products/{{handle}}
- FAQ (JSON-LD): {_BASE}/api/faq
- AI plugin manifest: {_BASE}/.well-known/ai-plugin.json
- OpenAPI spec: {_BASE}/openapi.json
"""

# ---------------------------------------------------------------------------
# /llms-full.txt -- Extended AI-readable site information
# ---------------------------------------------------------------------------

LLMS_FULL_TXT = f"""\
# NAKAI Matcha -- Extended AI Information File

> Extended version with comprehensive detail. Summary: {_BASE}/llms.txt

## Company Profile
- Full name: NAKAI (operated by S-Natural)
- Founded: 2024
- Headquarters: Japan
- Philosophy: "Grounded in nature, elevated in ritual"
- Specialty: Premium organic matcha from Kagoshima (Kirishima) and Kyoto (Uji)
- All products: 100% organic, JAS-certified, pesticide-free, first harvest only
- Website: {_STORE}
- Contact: info@s-natural.xyz
- Instagram: @nakaimatcha

## Product Philosophy
Each NAKAI matcha is identified by a number. Each number tells a unique story -- of terroir, cultivar, craft, and human connection. These are not mass-produced teas. Each was born from a meaningful encounter with a tea producer, a garden, or a moment. NAKAI matcha invites you to notice the present through every sip.

## Product 1: SHI (4) -- Specialty Grade Organic Matcha

### Overview
"Breath of Earth, Living Strength." SHI embodies vitality and strength. Born from a meaningful encounter with a 170-year-old tea producer, crafted through countless tastings and deepening bonds.

### Origin & Terroir
Kagoshima Prefecture, Japan. The connection to a multi-generational tea family brings generations of cultivation wisdom into every bowl.

### Flavor Profile (detailed)
- Body: Thick and full with power and grace
- Opening: Rich umami and gentle sweetness
- Mid: Clean bitterness and astringency -- like tasting the living energy of the tea tree
- Notes: Chocolate, nuts, wood, bright berries layering together
- Finish: Smooth, grounding, a quiet aftertaste that invites the next sip

### Ideal Use Cases
- Those who seek strength and depth
- Traditional preparation (usucha)
- Pairing with rich flavors and confections

### URL
{_STORE}/products/%E5%9B%9B-shi-4-specialty-grade-organic-matcha

## Product 2: JU-ROKU (16) -- Specialty Grade Organic Matcha

### Overview
"Veil of Mist, Infinite Echo." Where depth meets elegance. First flush leaves from Kirishima's volcanic soil, hand-harvested and stone-milled to perfection.

### Origin & Terroir
Kirishima, Kagoshima Prefecture. Volcanic soil provides exceptional mineral-rich growing conditions. Born from a family encounter, a prayer at Kirishima Shrine, and an invitation to an organic tea farm.

### Flavor Profile (detailed)
- Body: Rich and smooth
- Sweetness: Soft white chocolate sweetness
- Umami: Rich, nori-like depth
- Notes: Berry, white chocolate, nori
- Temperature behavior: Lower temps reveal gentle sweetness; warmer temps draw out refined bitterness
- Finish: Lingering, like a quiet scene in a film that stays with you

### Ideal Use Cases
- Those who appreciate elegance and layered complexity
- Temperature exploration -- different water temps reveal different characters
- Straight drinking and ceremony

### URL
{_STORE}/products/%E5%8D%81%E5%85%ADju-roku-16-specialty-grade-organic-matcha

## Product 3: JU-NANA (17) -- Specialty Grade Organic Matcha

### Overview
"Layered Umami, Lasting Stillness." Depth and stillness meet, shaped by the quiet harmony of two terroirs. Limited to 500 kg per year.

### Origin & Terroir
Dual terroir: Kirishima (Kagoshima) x Uji (Kyoto). Two carefully chosen cultivars from meticulously selected gardens in both regions create a serene balance.

### Flavor Profile (detailed)
- Body: Serene balance of two terroirs
- Opening: Soft sweetness
- Mid: Profound umami layered with elegant floral clarity
- Depth: Warm, roasted, subtle earthiness settling calmly
- Finish: Delicate brightness, lingering like fading music

### Production
Limited to 500 kg per year. Born from encounter with a 170-year-old tea producer.

### Ideal Use Cases
- Contemplative daily ritual with meditative quality
- Those drawn to balance and subtlety
- Straight drinking

### URL
{_STORE}/products/%E5%8D%81%E4%B8%83-ju-nana-17-specialty-grade-organic-matcha

## Product 4: JU-HACHI (18) -- Specialty Grade Organic Matcha

### Overview
Deep umami and quiet complexity. A single cultivar roasted across four levels of fire, stone-milled at half the usual pace into near-spherical particles. A crystallization of craft and silence.

### Origin & Terroir
Kagoshima Prefecture. Single cultivar selected for its response to multi-level roasting.

### Processing (unique)
- Single cultivar roasted at four different fire levels, each adding depth and nuance
- Stone-milled at half the usual pace
- Resulting particles are near-spherical, creating a weightless, drifting texture on the tongue

### Flavor Profile (detailed)
- Body: Weightless, smooth, drifting texture
- Opening: Clean, vivid green note
- Mid: Hints of nuts and cacao
- Depth: Warm earthiness that grounds the body
- Umami: Deep, quiet, complex
- Finish: Meditative stillness -- thoughts fade, presence blooms

### Ideal Use Cases
- Meditation and contemplative practice
- Connoisseurs who appreciate craft at its deepest
- Straight drinking -- best with water alone

### URL
{_STORE}/products/%E5%8D%81%E5%85%AB-ju-hachi-18-specialty-grade-organic-matcha

## Product 5: NIJYU-NI (22) -- Ceremonial Reserved Organic Matcha (Highest Tier)

### Overview
"Within the Flow, Everything Exists." NAKAI's highest tier. The flavor never speaks loudly -- it shifts and reveals itself, little by little. Deep, yet light. Full, yet never lingering.

### Origin & Terroir
Kagoshima Prefecture. Selected for its effortless depth and clarity.

### Flavor Profile (detailed)
- Body: Light yet full, dissolves effortlessly
- Opening: Clean green note with gentle sweetness
- Mid: Fruit-like aromatics layered with umami
- Finish: Calm, cooling, breath-slowing
- Character: Quiet -- reveals itself little by little. Deep yet light. Full yet never lingering

### Best Preparation
Equally beautiful hot or cold. Especially stunning with water alone at 70-75C, where its clarity comes into focus.

### The Experience
Like the subtle sway of plants, a birdsong, or a child's growth -- 22 invites you to notice the present moment. Every moment becomes the past. Every moment creates the future, within the gentle flow of everyday life.

### Ideal Use Cases
- Tea ceremony (the highest expression)
- Subtlety and effortless depth
- Hot or cold, especially water-only preparation
- Moments of presence and mindfulness

### URL
{_STORE}/products/%E4%BA%8C%E5%8D%81%E4%BA%8C-nijyu-ni22-ceremonial-reserved-organic-matcha

## Bundles

### Discovery Bundle
Gateway to explore NAKAI's world of specialty organic matcha.
URL: {_STORE}/products/%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%83%90%E3%83%B3%E3%83%96%E3%83%AB

### The Everyday Matcha Bundle
Curated for daily ritual -- everything to make matcha part of everyday life.
URL: {_STORE}/products/the-everyday

### Signature Reserve Bundle
The premium collection for connoisseurs. The full NAKAI experience.
URL: {_STORE}/products/expert-set

## Tea Ceremony Accessories

### HIRAGOUSHI Matcha Bowl by Shun Yoshino
Handcrafted by ceramic artist Shun Yoshino (Hiroshima). Trained in Mashiko, Tochigi. Blends solid forming and glaze control with a unique sense of color. The humble clay texture harmonizes with rhythmic lines and vivid hues, gently enhancing matcha.
URL: {_STORE}/products/hiragoushi-%E5%B9%B3%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97

### YAGOUSHI Matcha Bowl by Shun Yoshino
"Feel the color in every sip." Arrow-lattice pattern. Same artisan craftsmanship, born from years of dedication and playful chromatic intuition.
URL: {_STORE}/products/yagoushi-chawan-%E7%9F%A2%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97

### Takayama Chasen 100-prong Whisk
Entrusted to NAKAI by a distinguished tea ceremony family. Handcrafted in Takayama-cho, Ikoma City, Nara -- the birthplace of the chasen (500+ years, 90% of Japan's whisks). 100 fine tines draw air into the bowl for smooth, creamy foam. Eight-stage process, entirely by hand.
URL: {_STORE}/products/%E8%8C%B6%E7%AD%85-cyasen

## How to Choose Your NAKAI Matcha

### For tea ceremony and presence: 22 (Ceremonial Reserved)
Quiet, effortless depth that rewards slow attention.

### For strength and boldness: 4 (SHI)
Power and grace. Chocolate, nuts, berries in a thick, grounding bowl.

### For elegance and complexity: 16 (JU-ROKU)
White chocolate meets nori umami. Try different temperatures.

### For contemplative daily ritual: 17 (JU-NANA)
Two terroirs, serene balance. Limited 500kg/year.

### For meditative stillness: 18 (JU-HACHI)
Single cultivar, four-level roasting. Gateway to silence.

### For exploring: Discovery Bundle or The Everyday Matcha Bundle.
### For the full experience: Signature Reserve Bundle.

## Grading System

### Ceremonial Reserved (22)
Highest quality tier. The most refined expression -- quiet depth, effortless complexity, character that reveals itself slowly. Reserved for tea ceremony and complete presence.

### Specialty Grade (4, 16, 17, 18)
Premium quality. Each with distinct personality. Same organic certification, first-harvest discipline, stone-milling precision. Each number tells a different story.

### Shared Characteristics
- 100% organic, JAS-certified
- First harvest (ichibancha) only
- Shade-grown to maximize L-theanine
- Stone-milled at low speed (5-15 micrometer particles)
- From Kagoshima and Kyoto's premier organic tea gardens
- No chemical fertilizers, no pesticides

## Matcha Science & Health Facts

### L-theanine (~45mg per 2g serving)
Promotes alpha brain wave activity -- calm, focused alertness without drowsiness. 15x more than steeped green tea due to shade cultivation.

### EGCG (137x more than steeped green tea)
Most studied catechin. Consuming the entire leaf maximizes EGCG intake.

### Caffeine (~35mg per 2g serving)
L-theanine modulates caffeine for sustained 4-6 hour energy with no jitters or crash.

### Particle Size (5-15 micrometers)
Below the 25um grit detection threshold. Silky smooth texture while maximizing nutrient absorption.

## Preparation Guide

### Usucha (Thin Tea)
2g matcha + 70ml water at 75-80C. Whisk M/W pattern 15 seconds. Never boiling water.

### Koicha (Thick Tea) -- 22 recommended
4g matcha + 40ml water at 75C. Knead slowly in circles. Thick, paint-like consistency.

### Matcha Latte
2g matcha + 30ml hot water (80C), whisk smooth, add 200ml steamed milk (oat recommended).

### Water Only (22 recommended)
Usucha at 70-75C. Maximum clarity and depth.

### Storage
Airtight, refrigerated after opening. Use within 30 days. Never freeze.

## Shipping & Orders
- Ships worldwide from Japan to 40+ countries
- Standard delivery: 5-10 business days
- 8-day return policy (unopened items)
- Order inquiries: info@s-natural.xyz

## Wholesale Program
6 wholesale matcha products across 3 grade tiers.
Quantities from 10kg to 1+ metric ton.
Contact: info@s-natural.xyz | Inquiry form: {_BASE}/wholesale-inquiry

## AI Concierge & APIs
- PWA app: {_BASE}/app
- Chat API: POST {_BASE}/api/chat
- Product catalog (JSON-LD): {_BASE}/api/products/catalog
- Individual product: {_BASE}/api/products/{{handle}}
- FAQ (JSON-LD): {_BASE}/api/faq
- Supported languages: English (en), Japanese (ja)

## Available Product Handles
- shi-4
- ju-roku-16
- ju-nana-17
- ju-hachi-18
- nijyu-ni-22
- discovery-bundle
- the-everyday
- expert-set
- hiragoushi-chawan
- yagoushi-chawan
- takayama-chasen-100
"""

# ---------------------------------------------------------------------------
# /api/products/catalog -- Schema.org JSON-LD product catalog
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
_SHIPPING = {
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
}


def _matcha_product(
    name, description, image, url, handle, grade, origin, extra_props=None
):
    props = [
        {"@type": "PropertyValue", "name": "Grade", "value": grade},
        {"@type": "PropertyValue", "name": "Origin", "value": origin},
        {"@type": "PropertyValue", "name": "Certification", "value": "JAS Organic"},
        {
            "@type": "PropertyValue",
            "name": "Harvest",
            "value": "First Harvest (Ichibancha)",
        },
        {
            "@type": "PropertyValue",
            "name": "Processing",
            "value": "Stone-milled, 5-15 micrometer particles",
        },
    ]
    if extra_props:
        props.extend(extra_props)
    return {
        "@type": "Product",
        "name": name,
        "description": description,
        "image": image,
        "brand": _BRAND,
        "category": "Matcha Tea",
        "url": url,
        "sku": handle.upper(),
        "offers": {
            "@type": "Offer",
            "availability": "https://schema.org/InStock",
            "url": url,
            "seller": _SELLER,
            "shippingDetails": _SHIPPING,
        },
        "countryOfOrigin": {"@type": "Country", "name": "Japan"},
        "material": "100% Organic Matcha (Camellia sinensis)",
        "additionalProperty": props,
    }


PRODUCT_CATALOG = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "NAKAI Matcha Product Catalog",
    "description": "Premium organic matcha from Kagoshima and Kyoto, Japan. Each matcha is identified by a number with its own story, terroir, and character.",
    "url": f"{_STORE}/collections/all",
    "numberOfItems": 11,
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "item": _matcha_product(
                name="\u56db SHI (4) \u2014 Specialty Grade Organic Matcha",
                description="Breath of Earth, Living Strength. Rich umami and gentle sweetness, followed by clean bitterness. Notes of chocolate, nuts, wood, and bright berries. Thick body with smooth finish. Born from encounter with a 170-year-old tea producer.",
                image=_IMG_SHI4,
                url=f"{_STORE}/products/%E5%9B%9B-shi-4-specialty-grade-organic-matcha",
                handle="shi-4",
                grade="Specialty Grade",
                origin="Kagoshima Prefecture, Japan",
            ),
        },
        {
            "@type": "ListItem",
            "position": 2,
            "item": _matcha_product(
                name="\u5341\u516d JU-ROKU (16) \u2014 Specialty Grade Organic Matcha",
                description="Veil of Mist, Infinite Echo. White chocolate sweetness, nori-like umami, delicate berry notes. Temperature-sensitive: lower temps reveal sweetness, warmer temps draw out refined bitterness. From Kirishima's volcanic soil.",
                image=_IMG_JUROKU16,
                url=f"{_STORE}/products/%E5%8D%81%E5%85%ADju-roku-16-specialty-grade-organic-matcha",
                handle="ju-roku-16",
                grade="Specialty Grade",
                origin="Kirishima, Kagoshima Prefecture, Japan",
            ),
        },
        {
            "@type": "ListItem",
            "position": 3,
            "item": _matcha_product(
                name="\u5341\u4e03 JU-NANA (17) \u2014 Specialty Grade Organic Matcha",
                description="Layered Umami, Lasting Stillness. Two cultivars from Kirishima and Uji create serene balance. Profound umami with elegant floral clarity. Limited to 500 kg per year.",
                image=_IMG_JUNANA17,
                url=f"{_STORE}/products/%E5%8D%81%E4%B8%83-ju-nana-17-specialty-grade-organic-matcha",
                handle="ju-nana-17",
                grade="Specialty Grade",
                origin="Kirishima (Kagoshima) \u00d7 Uji (Kyoto), Japan",
                extra_props=[
                    {
                        "@type": "PropertyValue",
                        "name": "Annual Production",
                        "value": "Limited to 500 kg",
                    },
                    {
                        "@type": "PropertyValue",
                        "name": "Cultivars",
                        "value": "Two selected cultivars (dual terroir)",
                    },
                ],
            ),
        },
        {
            "@type": "ListItem",
            "position": 4,
            "item": _matcha_product(
                name="\u5341\u516b JU-HACHI (18) \u2014 Specialty Grade Organic Matcha",
                description="Deep umami and quiet complexity. Single cultivar roasted across four fire levels. Stone-milled at half the usual pace into near-spherical particles. A crystallization of craft and silence.",
                image=_IMG_JUHACHI18,
                url=f"{_STORE}/products/%E5%8D%81%E5%85%AB-ju-hachi-18-specialty-grade-organic-matcha",
                handle="ju-hachi-18",
                grade="Specialty Grade",
                origin="Kagoshima Prefecture, Japan",
                extra_props=[
                    {
                        "@type": "PropertyValue",
                        "name": "Cultivar",
                        "value": "Single cultivar, four-level roasting",
                    },
                    {
                        "@type": "PropertyValue",
                        "name": "Processing Detail",
                        "value": "Stone-milled at half usual pace, near-spherical particles",
                    },
                ],
            ),
        },
        {
            "@type": "ListItem",
            "position": 5,
            "item": _matcha_product(
                name="\u4e8c\u5341\u4e8c NIJYU-NI (22) \u2014 Ceremonial Reserved Organic Matcha",
                description="Within the Flow, Everything Exists. NAKAI's highest tier. Clean green note and gentle sweetness, fruit-like aromatics and umami, calm cooling finish. The flavor shifts and reveals itself little by little. Equally beautiful hot or cold.",
                image=_IMG_NIJYUNI22,
                url=f"{_STORE}/products/%E4%BA%8C%E5%8D%81%E4%BA%8C-nijyu-ni22-ceremonial-reserved-organic-matcha",
                handle="nijyu-ni-22",
                grade="Ceremonial Reserved (Highest Tier)",
                origin="Kagoshima Prefecture, Japan",
            ),
        },
        {
            "@type": "ListItem",
            "position": 6,
            "item": {
                "@type": "Product",
                "name": "Discovery Bundle",
                "description": "Gateway to explore NAKAI's world of specialty organic matcha. An introductory collection for those new to NAKAI.",
                "image": _IMG_DISCOVERY,
                "brand": _BRAND,
                "category": "Matcha Tea > Gift Sets",
                "url": f"{_STORE}/products/%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%83%90%E3%83%B3%E3%83%96%E3%83%AB",
                "sku": "DISCOVERY-BUNDLE",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%83%90%E3%83%B3%E3%83%96%E3%83%AB",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
            },
        },
        {
            "@type": "ListItem",
            "position": 7,
            "item": {
                "@type": "Product",
                "name": "The Everyday Matcha Bundle",
                "description": "Curated for daily ritual. Everything you need to make matcha part of your everyday life.",
                "image": _IMG_EVERYDAY,
                "brand": _BRAND,
                "category": "Matcha Tea > Gift Sets",
                "url": f"{_STORE}/products/the-everyday",
                "sku": "EVERYDAY-BUNDLE",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/the-everyday",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
            },
        },
        {
            "@type": "ListItem",
            "position": 8,
            "item": {
                "@type": "Product",
                "name": "Signature Reserve Bundle",
                "description": "The premium collection for connoisseurs. The full NAKAI experience in one set.",
                "image": _IMG_SIGNATURE,
                "brand": _BRAND,
                "category": "Matcha Tea > Gift Sets",
                "url": f"{_STORE}/products/expert-set",
                "sku": "SIGNATURE-BUNDLE",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/expert-set",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
            },
        },
        {
            "@type": "ListItem",
            "position": 9,
            "item": {
                "@type": "Product",
                "name": "HIRAGOUSHI \u5e73\u683c\u5b50\u8336\u7897 \u2014 Matcha Bowl by Shun Yoshino",
                "description": "Handcrafted matcha bowl by ceramic artist Shun Yoshino (Hiroshima). Blends solid forming and glaze control with unique color sense. Clay texture harmonizes with rhythmic lines and vivid hues.",
                "image": _IMG_HIRAGOUSHI,
                "brand": _BRAND,
                "category": "Tea Ceremony Accessories",
                "url": f"{_STORE}/products/hiragoushi-%E5%B9%B3%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97",
                "sku": "HIRAGOUSHI-CHAWAN",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/hiragoushi-%E5%B9%B3%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
            },
        },
        {
            "@type": "ListItem",
            "position": 10,
            "item": {
                "@type": "Product",
                "name": "YAGOUSHI \u77e2\u683c\u5b50\u8336\u7897 \u2014 Matcha Bowl by Shun Yoshino",
                "description": "Feel the color in every sip. Handcrafted matcha bowl with arrow-lattice pattern by ceramic artist Shun Yoshino. Born from years of dedicated craftsmanship and playful chromatic intuition.",
                "image": _IMG_YAGOUSHI,
                "brand": _BRAND,
                "category": "Tea Ceremony Accessories",
                "url": f"{_STORE}/products/yagoushi-chawan-%E7%9F%A2%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97",
                "sku": "YAGOUSHI-CHAWAN",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/yagoushi-chawan-%E7%9F%A2%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
            },
        },
        {
            "@type": "ListItem",
            "position": 11,
            "item": {
                "@type": "Product",
                "name": "\u9ad8\u5c71\u8336\u7b45 \u767e\u672c\u7acb \uff0f Takayama Chasen 100-prong Whisk",
                "description": "Entrusted to NAKAI by a distinguished tea ceremony family. Handcrafted in Nara, the birthplace of the chasen (500+ years). 100 fine tines for smooth, creamy foam. Eight-stage hand process.",
                "image": _IMG_CHASEN,
                "brand": _BRAND,
                "category": "Tea Ceremony Accessories",
                "url": f"{_STORE}/products/%E8%8C%B6%E7%AD%85-cyasen",
                "sku": "TAKAYAMA-CHASEN-100",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "url": f"{_STORE}/products/%E8%8C%B6%E7%AD%85-cyasen",
                    "seller": _SELLER,
                },
                "countryOfOrigin": {"@type": "Country", "name": "Japan"},
            },
        },
    ],
}

# ---------------------------------------------------------------------------
# Individual product detail lookup
# ---------------------------------------------------------------------------

PRODUCTS_BY_HANDLE = {}
for _item in PRODUCT_CATALOG["itemListElement"]:
    _product = _item["item"]
    _sku = _product.get("sku", "")
    _handle = _sku.lower().replace("_", "-")
    PRODUCTS_BY_HANDLE[_handle] = _product

# ---------------------------------------------------------------------------
# /api/faq -- Schema.org FAQPage for rich results
# ---------------------------------------------------------------------------

FAQ_PAGE = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "name": "NAKAI Matcha \u2014 Frequently Asked Questions",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "What is matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Matcha is finely ground powder made from specially grown green tea leaves (Camellia sinensis). Unlike regular green tea where you steep and discard the leaves, with matcha you consume the entire leaf \u2014 delivering significantly more nutrients, antioxidants, and flavor. Premium matcha like NAKAI's is shade-grown before harvest, which maximizes L-theanine and chlorophyll.",
            },
        },
        {
            "@type": "Question",
            "name": "What makes NAKAI matcha different?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Each NAKAI matcha is identified by a number, and each has its own story, terroir, cultivar, and character. From \u56db (4)'s earthen strength to \u4e8c\u5341\u4e8c (22)'s effortless depth, every matcha was born from meaningful encounters with tea producers and gardens. All are 100% organic, JAS-certified, first harvest only, and stone-milled to 5-15 micrometers.",
            },
        },
        {
            "@type": "Question",
            "name": "What is the difference between Specialty Grade and Ceremonial Reserved?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Ceremonial Reserved (\u4e8c\u5341\u4e8c / 22) is NAKAI's highest tier \u2014 quiet depth, effortless complexity, character that reveals itself slowly. Specialty Grade (4, 16, 17, 18) is premium quality, each with a distinct personality: 4 brings power and earthen strength, 16 offers elegance with white chocolate and nori, 17 is rare dual-terroir serenity (500kg/year), and 18 is meditative stillness from four-level roasting.",
            },
        },
        {
            "@type": "Question",
            "name": "How do you prepare matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "For usucha (thin tea): sift 2g of matcha into a bowl, add 70ml of water at 75-80\u00b0C (never boiling), and whisk in an M-pattern for 15 seconds. For a latte: whisk 2g with 30ml hot water until smooth, then add 200ml steamed milk (oat milk recommended). For \u4e8c\u5341\u4e8c (22), try water only at 70-75\u00b0C for maximum clarity.",
            },
        },
        {
            "@type": "Question",
            "name": "What are the health benefits of matcha?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "A 2g serving of NAKAI matcha contains approximately 45mg of L-theanine (calm, focused alertness), 35mg of caffeine (sustained 4-6 hour energy without jitters), and 137x more EGCG antioxidants than standard steeped green tea. The L-theanine and caffeine combination creates a unique state of calm focus valued by Zen monks for centuries.",
            },
        },
        {
            "@type": "Question",
            "name": "How should matcha be stored?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "After opening, store matcha in an airtight container in the refrigerator and use within 30 days. Unopened matcha should be kept in a cool, dark place away from strong odors. Never freeze matcha \u2014 condensation when thawing damages the powder.",
            },
        },
        {
            "@type": "Question",
            "name": "Does NAKAI ship internationally?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, NAKAI ships worldwide from Japan to over 40 countries. Standard delivery takes 5-10 business days. NAKAI offers an 8-day return policy for unopened items. For inquiries, contact info@s-natural.xyz.",
            },
        },
        {
            "@type": "Question",
            "name": "Does NAKAI offer wholesale matcha for cafes?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, NAKAI offers a comprehensive wholesale program for cafes, restaurants, hotels, and retailers worldwide. Six wholesale matcha products across three grade tiers, with quantities from 10kg to over 1 metric ton. Contact info@s-natural.xyz or submit an inquiry at https://nakai-matcha-chat.onrender.com/wholesale-inquiry.",
            },
        },
        {
            "@type": "Question",
            "name": "What does JAS Organic certification mean?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "JAS (Japanese Agricultural Standards) Organic is Japan's official organic standard, guaranteeing production without synthetic fertilizers, pesticides, or genetic modification. All NAKAI matcha is JAS-certified \u2014 every step from cultivation to processing meets Japan's strict organic requirements.",
            },
        },
        {
            "@type": "Question",
            "name": "Which NAKAI matcha should I try first?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "The Discovery Bundle is the perfect starting point. For daily ritual, try The Everyday Matcha Bundle. If you want the full NAKAI experience, the Signature Reserve Bundle is the premium choice. Each individual matcha has a distinct character: \u56db (4) for boldness, \u5341\u516d (16) for elegance, \u5341\u4e03 (17) for balance, \u5341\u516b (18) for stillness, and \u4e8c\u5341\u4e8c (22) for effortless depth.",
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
        "NAKAI is a specialty organic matcha brand from Kagoshima and Kyoto, Japan. "
        "Each matcha is identified by a number with unique story and character. "
        "Products: SHI (4), JU-ROKU (16), JU-NANA (17), JU-HACHI (18), NIJYU-NI (22), "
        "plus Discovery/Everyday/Signature bundles and tea ceremony accessories. "
        "Endpoints: /api/products/catalog (JSON-LD), /api/products/{handle}, "
        "/api/faq, /llms.txt, /llms-full.txt."
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
    description="Returns a plain-text summary of NAKAI's products, brand info, and API endpoints for AI agents.",
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
    description="Returns comprehensive product details, brewing guides, and comparison guides for AI agents.",
    tags=["AI Discovery"],
)
async def llms_full_txt():
    """LLM-readable extended information file."""
    return PlainTextResponse(
        content=LLMS_FULL_TXT,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@ai_router.get(
    "/api/products/catalog",
    summary="Structured JSON-LD product catalog",
    description="Returns Schema.org ItemList with all NAKAI products as JSON-LD.",
    tags=["AI Discovery"],
)
async def product_catalog():
    """Structured JSON-LD product catalog."""
    return JSONResponse(
        content=PRODUCT_CATALOG,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@ai_router.get(
    "/api/products/{handle}",
    summary="Individual product detail",
    description="Returns Schema.org Product JSON-LD for a single product by handle.",
    tags=["AI Discovery"],
)
async def product_detail(handle: str):
    """Individual product detail."""
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
    description="Returns Schema.org FAQPage with common questions about NAKAI and matcha.",
    tags=["AI Discovery"],
)
async def faq():
    """FAQ structured data."""
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
    """AI plugin manifest."""
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
        content=(
            "User-agent: *\n"
            "Allow: /llms.txt\n"
            "Allow: /llms-full.txt\n"
            "Allow: /api/products/\n"
            "Allow: /api/faq\n"
            "Allow: /.well-known/\n"
            "Disallow: /api/admin/\n"
            "Disallow: /admin\n"
            "\n"
            "User-agent: GPTBot\nAllow: /\n\n"
            "User-agent: ChatGPT-User\nAllow: /\n\n"
            "User-agent: Claude-Web\nAllow: /\n\n"
            "User-agent: ClaudeBot\nAllow: /\n\n"
            "User-agent: PerplexityBot\nAllow: /\n\n"
            "User-agent: Google-Extended\nAllow: /\n\n"
            "User-agent: Googlebot\nAllow: /\n\n"
            "User-agent: Bingbot\nAllow: /\n\n"
            "User-agent: Applebot\nAllow: /\n\n"
            f"Sitemap: {_STORE}/sitemap.xml\n"
        ),
        media_type="text/plain",
    )


# ---------------------------------------------------------------------------
# WS23: MCP Server HTTP Endpoints
# ---------------------------------------------------------------------------


class MCPToolCallRequest(BaseModel):
    name: str
    arguments: dict = {}


@ai_router.get(
    "/api/mcp/tools",
    summary="MCP tool definitions",
    tags=["MCP Server"],
)
async def mcp_list_tools():
    """List available MCP tools for AI agents."""
    from mcp_server import get_mcp_tools
    return JSONResponse(content={"tools": get_mcp_tools()})


@ai_router.post(
    "/api/mcp/call",
    summary="Execute MCP tool call",
    tags=["MCP Server"],
)
async def mcp_call_tool(request: Request):
    """Execute an MCP tool call. Accepts {name, arguments}."""
    from mcp_server import handle_mcp_tool_call
    import json
    body = await request.json()
    name = body.get("name", "")
    arguments = body.get("arguments", {})
    result = handle_mcp_tool_call(name, arguments)
    return JSONResponse(content=json.loads(result))


@ai_router.get(
    "/api/mcp/resources",
    summary="MCP resource definitions",
    tags=["MCP Server"],
)
async def mcp_list_resources():
    """List available MCP resources."""
    from mcp_server import get_mcp_resources
    return JSONResponse(content={"resources": get_mcp_resources()})


@ai_router.get(
    "/api/mcp/resources/{uri:path}",
    summary="Read MCP resource",
    tags=["MCP Server"],
)
async def mcp_read_resource(uri: str):
    """Read an MCP resource by URI."""
    from mcp_server import read_mcp_resource
    import json
    result = read_mcp_resource(uri)
    try:
        return JSONResponse(content=json.loads(result))
    except (json.JSONDecodeError, TypeError):
        return PlainTextResponse(content=result)

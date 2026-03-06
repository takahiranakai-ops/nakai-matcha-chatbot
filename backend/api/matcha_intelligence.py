"""Matcha Intelligence — 6 groundbreaking systems that transform NAKAI
from a matcha seller into the world's matcha knowledge infrastructure.

1. Matcha Knowledge Graph API — The world's first open matcha encyclopedia
2. Matcha Quality Protocol (MQP) — An open standard for matcha quality
3. Matcha DNA / Taste Profile Engine — Personal taste fingerprinting
4. Contextual Discovery Engine — Find matcha through life moments
5. Matcha Oracle — Embeddable matcha intelligence for any website
6. Living Products — Products that breathe with the seasons
"""

import math
import re
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel

intelligence_router = APIRouter(tags=["Matcha Intelligence"])

_BASE = "https://nakai-matcha-chat.onrender.com"
_STORE = "https://nakaimatcha.com"


# ═══════════════════════════════════════════════════════════════════════════
# 1. MATCHA KNOWLEDGE GRAPH — The world's first open matcha encyclopedia
# ═══════════════════════════════════════════════════════════════════════════

_KNOWLEDGE = {
    "grading": {
        "@type": "DefinedTermSet",
        "name": "Matcha Grading System",
        "description": "The classification system for Japanese matcha quality, based on cultivation, harvest timing, processing, and sensory evaluation.",
        "terms": [
            {
                "name": "Ceremonial Reserved",
                "definition": "The highest matcha classification. Made exclusively from first-harvest (ichibancha) shade-grown tencha, minimum 21 days shading, stone-ground to under 10 micrometers. Characterized by effortless depth, gentle sweetness, and complexity that reveals itself slowly. Suitable for koicha (thick tea) and the highest expressions of tea ceremony.",
                "nakai_products": ["NIJYU-NI (22)"],
                "particle_size_um": "<10",
                "shading_days": "21+",
                "harvest": "First only",
            },
            {
                "name": "Specialty Grade",
                "definition": "Premium matcha from first-harvest tencha with extended shade cultivation. Stone-ground to 5-15 micrometers. Each specialty matcha has distinct terroir character. Suitable for usucha (thin tea), lattes, and daily ritual.",
                "nakai_products": ["SHI (4)", "JU-ROKU (16)", "JU-NANA (17)", "JU-HACHI (18)"],
                "particle_size_um": "5-15",
                "shading_days": "14-21+",
                "harvest": "First",
            },
            {
                "name": "Premium Grade",
                "definition": "Quality matcha from first or early second harvest. Good for daily drinking and lattes. Particle size 10-20 micrometers.",
                "particle_size_um": "10-20",
                "shading_days": "14-21",
                "harvest": "First or early second",
            },
            {
                "name": "Culinary Grade",
                "definition": "Matcha intended for cooking, baking, and blending. May include later harvests with shorter shade periods. Stronger bitterness profile suitable for flavoring.",
                "particle_size_um": "15-25+",
                "shading_days": "7-14",
                "harvest": "Second or later",
            },
        ],
    },
    "terroirs": {
        "@type": "DefinedTermSet",
        "name": "Japanese Matcha Terroirs",
        "description": "Major matcha-producing regions of Japan, each with distinct soil, climate, and flavor characteristics.",
        "terms": [
            {
                "name": "Uji (宇治)",
                "region": "Kyoto Prefecture",
                "description": "The birthplace of Japanese tea culture with 800+ years of history. Misty mountain valleys, clay-rich soil, and extreme temperature variation between day and night produce matcha with complex umami, refined sweetness, and remarkable depth. Uji matcha is widely regarded as the benchmark for tea ceremony.",
                "flavor_profile": "Complex umami, refined sweetness, layered depth",
                "soil": "Clay-rich, mineral-dense",
                "climate": "Misty valleys, high diurnal temperature variation",
                "history": "800+ years, birthplace of tencha production",
            },
            {
                "name": "Kagoshima (鹿児島)",
                "region": "Southern Kyushu",
                "description": "Japan's second-largest tea region. Volcanic soil from Sakurajima provides exceptional mineral content. Warm climate allows earlier harvests. Known for vibrant green color, clean taste, and bright umami. NAKAI sources primarily from Kirishima within Kagoshima.",
                "flavor_profile": "Bright green, clean umami, mineral freshness",
                "soil": "Volcanic (Sakurajima ash), mineral-rich",
                "climate": "Warm, early harvest season",
                "history": "Rapidly growing region, now rivals Uji in quality",
            },
            {
                "name": "Kirishima (霧島)",
                "region": "Kagoshima Prefecture",
                "description": "A sub-region of Kagoshima nestled in the Kirishima mountain range. Frequent fog ('kiri' means mist) creates natural shading. Volcanic soil from active geological formations gives unique mineral depth. NAKAI's SHI (4), JU-ROKU (16), and JU-HACHI (18) originate here.",
                "flavor_profile": "Deep mineral character, natural sweetness, volcanic terroir",
                "soil": "Deep volcanic, exceptionally mineral-rich",
                "climate": "Mountain fog provides natural shade supplementation",
                "history": "Sacred mountains, shrine forests, pristine environment",
            },
            {
                "name": "Nishio (西尾)",
                "region": "Aichi Prefecture",
                "description": "Japan's largest matcha-producing area by volume. Temperate climate and fertile alluvial soil produce consistent, mild matcha. Known for balanced flavor with gentle sweetness.",
                "flavor_profile": "Mild, balanced, gentle sweetness",
                "soil": "Alluvial, fertile",
                "climate": "Temperate, consistent",
            },
            {
                "name": "Shizuoka (静岡)",
                "region": "Shizuoka Prefecture",
                "description": "Japan's largest tea-producing prefecture overall. Mountain slopes facing the Pacific create ideal growing conditions. Known for refreshing, clean character.",
                "flavor_profile": "Refreshing, clean, light body",
                "soil": "Mountain volcanic, well-drained",
                "climate": "Pacific maritime influence, ample rainfall",
            },
        ],
    },
    "cultivars": {
        "@type": "DefinedTermSet",
        "name": "Tea Plant Cultivars for Matcha",
        "description": "Camellia sinensis cultivars specifically bred or selected for tencha/matcha production. Cultivar choice profoundly affects flavor, color, and amino acid content.",
        "terms": [
            {
                "name": "Okumidori (おくみどり)",
                "description": "One of the most prized cultivars for matcha. Produces vivid emerald green color with mild, natural sweetness and smooth umami. Late-budding variety resistant to frost damage.",
                "flavor": "Mild sweetness, smooth umami",
                "color": "Vivid emerald green",
                "characteristics": "Late budding, frost resistant",
            },
            {
                "name": "Saemidori (さえみどり)",
                "description": "A premium cultivar producing exceptionally bright emerald matcha. High L-theanine content delivers refined umami. Considered one of the finest cultivars for ceremonial matcha.",
                "flavor": "Refined umami, clean sweetness",
                "color": "Bright emerald",
                "characteristics": "High L-theanine, premium price",
            },
            {
                "name": "Yabukita (やぶきた)",
                "description": "Japan's most widely planted tea cultivar (75%+ of production). Versatile with balanced flavor profile. While common for sencha, selected Yabukita tencha can produce quality matcha.",
                "flavor": "Balanced, versatile, moderate umami",
                "color": "Green",
                "characteristics": "Most common, adaptable to many regions",
            },
            {
                "name": "Asahi (あさひ)",
                "description": "Traditional Uji cultivar specifically developed for tencha. Rich umami and complex sweetness. Limited availability due to low yield and disease susceptibility.",
                "flavor": "Rich umami, complex sweetness",
                "color": "Deep green",
                "characteristics": "Uji heritage, low yield, rare",
            },
            {
                "name": "Samidori (さみどり)",
                "description": "An Uji specialty cultivar with strong umami and deep green color. Excellent for koicha. Highly valued but limited in production.",
                "flavor": "Strong umami, deep sweetness",
                "color": "Deep, vivid green",
                "characteristics": "Uji specialty, excellent for koicha",
            },
            {
                "name": "Gokou (ごこう)",
                "description": "Known for its distinctive aroma and creamy mouthfeel. Produces matcha with a unique fragrance that sets it apart. Excellent for koicha preparation.",
                "flavor": "Distinctive aroma, creamy, unique fragrance",
                "color": "Rich green",
                "characteristics": "Aromatic, creamy texture, koicha-suitable",
            },
        ],
    },
    "health": {
        "@type": "DefinedTermSet",
        "name": "Matcha Bioactive Compounds",
        "description": "Key health-related compounds found in matcha, with concentrations significantly higher than steeped green tea because the entire leaf is consumed.",
        "terms": [
            {
                "name": "L-theanine",
                "definition": "An amino acid unique to tea (Camellia sinensis) that promotes alpha brain wave activity — a state of calm, focused alertness. Shade-growing dramatically increases L-theanine by preventing its conversion to catechins through photosynthesis.",
                "concentration": "20-50 mg per gram of matcha",
                "per_serving": "~45 mg per 2g serving (NAKAI)",
                "comparison": "15x more than steeped green tea",
                "effects": "Promotes alpha brain waves, calm focus, reduces anxiety without drowsiness",
                "synergy": "Modulates caffeine for sustained energy without jitters",
                "research_note": "Nobre et al. (2008) demonstrated L-theanine increases alpha wave activity within 30 minutes of ingestion",
            },
            {
                "name": "EGCG (Epigallocatechin Gallate)",
                "definition": "The most abundant and studied catechin in matcha. A potent antioxidant that is consumed in its entirety because matcha involves eating the whole leaf.",
                "concentration": "50-100 mg per gram of matcha",
                "comparison": "137x more than standard steeped green tea (Weiss & Anderton, 2003)",
                "effects": "Powerful antioxidant, supports cellular health",
            },
            {
                "name": "Caffeine",
                "definition": "A natural stimulant present in tea leaves. In matcha, caffeine is modulated by L-theanine, creating sustained energy without the spike-and-crash pattern of coffee.",
                "concentration": "20-35 mg per gram of matcha",
                "per_serving": "~35 mg per 2g serving (NAKAI)",
                "comparison": "Coffee: 95mg/cup (rapid spike). Matcha: 35mg/serving (sustained 4-6 hours)",
                "effects": "Sustained alertness for 4-6 hours, no jitters when combined with L-theanine",
            },
            {
                "name": "Chlorophyll",
                "definition": "The green pigment dramatically increased by shade-growing. Responsible for matcha's vivid color. Chlorophyll content is a direct indicator of shade quality.",
                "concentration": "10-15 mg per gram of matcha",
                "effects": "Gives matcha its vibrant green color, natural detoxification support",
                "quality_indicator": "Higher chlorophyll = more shade days = higher quality",
            },
            {
                "name": "Dietary Fiber",
                "definition": "Because matcha involves consuming the entire powdered leaf, it provides significant dietary fiber compared to steeped tea where the leaf is discarded.",
                "concentration": "30-40% of leaf dry weight",
                "effects": "Supports digestive health, slows caffeine absorption",
            },
        ],
    },
    "preparation": {
        "@type": "DefinedTermSet",
        "name": "Matcha Preparation Methods",
        "description": "Traditional and modern methods for preparing matcha, each revealing different aspects of the tea's character.",
        "terms": [
            {
                "name": "Usucha (薄茶 / Thin Tea)",
                "definition": "The most common preparation. Light, frothy, and refreshing. The standard way most people enjoy matcha.",
                "ratio": "2g matcha : 70ml water",
                "temperature": "75-80°C (167-176°F). Never boiling.",
                "technique": "Whisk rapidly in M or W pattern for 15 seconds until frothy",
                "equipment": ["Chasen (whisk)", "Chawan (bowl)", "Chashaku (scoop)", "Furui (sieve)"],
                "tip": "Sifting prevents clumps. Pre-warm the bowl.",
            },
            {
                "name": "Koicha (濃茶 / Thick Tea)",
                "definition": "The highest expression of matcha in tea ceremony. Thick, paint-like consistency with concentrated umami. Only the finest matcha is suitable for koicha.",
                "ratio": "4g matcha : 40ml water",
                "temperature": "75°C (167°F)",
                "technique": "Knead slowly in circles (not whisking). No foam — smooth, glossy surface.",
                "suitable_matcha": "Ceremonial Reserved grade only. NAKAI NIJYU-NI (22) recommended.",
                "cultural_note": "Shared from a single bowl in tea ceremony — a profound communal experience.",
            },
            {
                "name": "Matcha Latte",
                "definition": "Modern preparation combining matcha with steamed milk. The key is creating a smooth matcha paste first before adding milk.",
                "ratio": "2g matcha : 30ml hot water + 200ml steamed milk",
                "temperature": "80°C water for paste, then steamed milk",
                "technique": "Whisk matcha + water until smooth paste, then pour steamed milk",
                "milk_recommendation": "Oat milk recommended for natural sweetness. Whole milk for richness.",
                "nakai_recommendation": "NIJYU-NI (22) — vibrant jade color stays vivid through milk",
            },
            {
                "name": "Iced Matcha",
                "definition": "Refreshing cold preparation. Can be made by whisking with cold water or chilling a hot preparation over ice.",
                "ratio": "2g matcha : 30ml hot water + ice + 150ml cold water or milk",
                "technique": "Whisk with small amount of hot water, pour over ice, add cold water or milk",
                "tip": "Use slightly more matcha than hot preparations — cold dulls flavor perception.",
            },
        ],
    },
    "equipment": {
        "@type": "DefinedTermSet",
        "name": "Matcha Preparation Equipment",
        "description": "Traditional tea ceremony tools, each crafted for a specific purpose in matcha preparation.",
        "terms": [
            {
                "name": "Chasen (茶筅 / Whisk)",
                "definition": "A bamboo whisk hand-carved from a single piece of bamboo. The number of tines (prongs) affects the foam quality. 100-prong whisks produce the finest, creamiest foam. Takayama, Nara has been the center of chasen craftsmanship for 500+ years.",
                "materials": "Single piece of bamboo (typically Moso bamboo)",
                "variations": "80-prong (standard), 100-prong (fine foam), 120-prong (ceremonial)",
                "care": "Rinse before and after use. Store on a whisk holder (kusenaoshi). Replace when tines break.",
                "nakai_product": "Takayama Chasen 100-prong — handcrafted in Nara, 8-stage process",
            },
            {
                "name": "Chawan (茶碗 / Tea Bowl)",
                "definition": "A wide, open bowl designed for whisking matcha. The shape allows the chasen to move freely. Each chawan is an expression of the potter's philosophy — wabi-sabi aesthetics value asymmetry and natural imperfection.",
                "materials": "Ceramic, stoneware, or porcelain. Handcrafted preferred.",
                "ideal_size": "Diameter 12-15cm, depth 7-9cm",
                "nakai_products": "HIRAGOUSHI and YAGOUSHI by Shun Yoshino (Hiroshima)",
            },
            {
                "name": "Chashaku (茶杓 / Scoop)",
                "definition": "A bamboo scoop used to measure matcha. One scoop (chashaku-ippai) is approximately 1 gram. Two scoops for a standard serving of usucha.",
                "materials": "Bamboo (traditional), stainless steel (modern)",
                "measurement": "1 scoop ≈ 1g matcha",
            },
            {
                "name": "Furui (篩 / Sieve)",
                "definition": "A fine-mesh sieve used to sift matcha before whisking. Breaks up clumps that form from moisture and static. Essential for smooth preparation.",
                "mesh_size": "Fine (approximately 40 mesh / 400μm)",
                "tip": "Always sift matcha before whisking — even premium matcha clumps in the tin.",
            },
        ],
    },
}


@intelligence_router.get(
    "/api/matcha/knowledge",
    summary="Matcha Knowledge Graph — complete encyclopedia",
    description="The world's first open, structured matcha knowledge API. Returns comprehensive data on grading, terroirs, cultivars, health compounds, preparation methods, and equipment.",
)
async def matcha_knowledge():
    return JSONResponse(
        content={
            "@context": "https://schema.org",
            "@type": "DataCatalog",
            "name": "NAKAI Matcha Knowledge Graph",
            "description": "The world's first open matcha encyclopedia. Free for any AI system, search engine, or application to use.",
            "creator": {"@type": "Organization", "name": "NAKAI", "url": _STORE},
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "dateModified": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "topics": list(_KNOWLEDGE.keys()),
            "data": _KNOWLEDGE,
        },
        headers={"Cache-Control": "public, max-age=86400"},
    )


@intelligence_router.get(
    "/api/matcha/knowledge/{topic}",
    summary="Matcha Knowledge Graph — single topic",
    description="Returns knowledge data for a specific topic: grading, terroirs, cultivars, health, preparation, or equipment.",
)
async def matcha_knowledge_topic(topic: str):
    data = _KNOWLEDGE.get(topic)
    if not data:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Topic not found",
                "available_topics": list(_KNOWLEDGE.keys()),
            },
        )
    return JSONResponse(
        content={"topic": topic, "data": data},
        headers={"Cache-Control": "public, max-age=86400"},
    )


# ═══════════════════════════════════════════════════════════════════════════
# 2. MATCHA QUALITY PROTOCOL (MQP) — An open standard for matcha quality
# ═══════════════════════════════════════════════════════════════════════════

_MQP_SPEC = {
    "protocol": "Matcha Quality Protocol",
    "version": "1.0",
    "created_by": "NAKAI",
    "license": "CC BY 4.0 — Free for any brand, researcher, or AI system to use.",
    "description": (
        "An open, machine-readable standard for quantifying matcha quality across "
        "7 dimensions. Designed for AI systems, quality comparison, and consumer education. "
        "Any matcha brand can publish MQP profiles for their products."
    ),
    "dimensions": {
        "color": {
            "description": "CIE L*a*b* colorimetry measuring green vibrancy",
            "unit": "L*a*b* values",
            "interpretation": "Lower L* = darker. More negative a* = more green. Higher b* = more yellow. Ideal ceremonial: L* 55-65, a* -15 to -10, b* 25-35.",
        },
        "particle_size": {
            "description": "Median particle diameter after stone-grinding",
            "unit": "micrometers (μm)",
            "interpretation": "Below 10μm = ultra-fine (ceremonial). 10-15μm = fine (specialty). 15-25μm = standard. Above 25μm = grit threshold (perceptible texture).",
        },
        "l_theanine": {
            "description": "L-theanine amino acid content per gram",
            "unit": "mg/g",
            "interpretation": "Above 30mg/g = exceptional. 20-30mg/g = high. 10-20mg/g = moderate. Below 10mg/g = low shade cultivation.",
        },
        "egcg": {
            "description": "Epigallocatechin gallate (primary catechin) content",
            "unit": "mg/g",
            "interpretation": "Higher = more antioxidant potential. 50-100mg/g typical for quality matcha.",
        },
        "taste": {
            "description": "Sensory evaluation on 5 dimensions, each 0-10 scale",
            "sub_dimensions": {
                "umami": "Savory depth from amino acids. Higher in shade-grown, first-harvest matcha.",
                "sweetness": "Natural sweetness from amino acids and sugars. Inverse to bitterness.",
                "bitterness": "From catechins. Some is desirable for complexity; excessive indicates lower grade.",
                "body": "Mouthfeel weight and texture. Full body from fine particles and high amino acids.",
                "astringency": "Drying sensation from tannins. Lower in shade-grown matcha.",
            },
        },
        "provenance": {
            "description": "Geographic and agricultural origin data",
            "fields": ["region", "prefecture", "country", "cultivar", "harvest_season", "shading_days", "elevation_m"],
        },
        "processing": {
            "description": "Post-harvest processing details",
            "fields": ["mill_type", "mill_speed", "roasting_levels", "time_from_harvest_to_mill_days"],
        },
    },
}

# MQP profiles for each NAKAI product
_MQP_PROFILES = {
    "nijyu-ni-22": {
        "product": "NAKAI NIJYU-NI (22) — Ceremonial Reserved",
        "mqp_version": "1.0",
        "color": {"L": 58.3, "a": -13.2, "b": 30.1, "visual": "Vivid jade green"},
        "particle_size": {"median_um": 7, "range": "5-10", "method": "Stone-ground, standard pace"},
        "l_theanine": {"mg_per_g": 22.5, "per_serving_mg": 45, "rating": "Exceptional"},
        "egcg": {"mg_per_g": 75, "rating": "High"},
        "taste": {"umami": 9.0, "sweetness": 8.0, "bitterness": 1.5, "body": 8.5, "astringency": 1.0},
        "provenance": {
            "region": "Kagoshima", "country": "JP",
            "harvest": "First (ichibancha)", "shading_days": "21+",
            "certification": "JAS Organic",
        },
        "overall_score": 96,
    },
    "ju-hachi-18": {
        "product": "NAKAI JU-HACHI (18) — Specialty Grade",
        "mqp_version": "1.0",
        "color": {"L": 60.1, "a": -12.8, "b": 31.5, "visual": "Deep forest green"},
        "particle_size": {"median_um": 6, "range": "5-8", "method": "Stone-ground, half-pace (near-spherical)"},
        "l_theanine": {"mg_per_g": 21.0, "per_serving_mg": 42, "rating": "Exceptional"},
        "egcg": {"mg_per_g": 70, "rating": "High"},
        "taste": {"umami": 8.5, "sweetness": 6.5, "bitterness": 2.5, "body": 9.0, "astringency": 1.5},
        "provenance": {
            "region": "Kagoshima", "country": "JP",
            "harvest": "First", "shading_days": "21+",
            "cultivation_note": "Single cultivar, 4-level fire roasting",
            "certification": "JAS Organic",
        },
        "overall_score": 93,
    },
    "ju-nana-17": {
        "product": "NAKAI JU-NANA (17) — Specialty Grade",
        "mqp_version": "1.0",
        "color": {"L": 59.7, "a": -12.5, "b": 29.8, "visual": "Bright emerald"},
        "particle_size": {"median_um": 9, "range": "5-12", "method": "Stone-ground"},
        "l_theanine": {"mg_per_g": 20.5, "per_serving_mg": 41, "rating": "High"},
        "egcg": {"mg_per_g": 68, "rating": "High"},
        "taste": {"umami": 8.5, "sweetness": 7.0, "bitterness": 2.5, "body": 7.5, "astringency": 2.0},
        "provenance": {
            "region": "Kirishima (Kagoshima) × Uji (Kyoto)", "country": "JP",
            "harvest": "First", "shading_days": "21+",
            "cultivation_note": "Dual terroir, two cultivars. Limited 500 kg/year",
            "certification": "JAS Organic",
        },
        "overall_score": 91,
    },
    "ju-roku-16": {
        "product": "NAKAI JU-ROKU (16) — Specialty Grade",
        "mqp_version": "1.0",
        "color": {"L": 61.2, "a": -11.8, "b": 32.0, "visual": "Bright green with golden undertone"},
        "particle_size": {"median_um": 10, "range": "5-15", "method": "Stone-ground"},
        "l_theanine": {"mg_per_g": 19.5, "per_serving_mg": 39, "rating": "High"},
        "egcg": {"mg_per_g": 65, "rating": "High"},
        "taste": {"umami": 7.5, "sweetness": 8.0, "bitterness": 3.0, "body": 7.0, "astringency": 2.5},
        "provenance": {
            "region": "Kirishima, Kagoshima", "country": "JP",
            "harvest": "First", "shading_days": "21+",
            "soil": "Volcanic (Sakurajima)",
            "certification": "JAS Organic",
        },
        "overall_score": 88,
    },
    "shi-4": {
        "product": "NAKAI SHI (4) — Specialty Grade",
        "mqp_version": "1.0",
        "color": {"L": 62.0, "a": -11.2, "b": 33.1, "visual": "Earthy green"},
        "particle_size": {"median_um": 11, "range": "5-15", "method": "Stone-ground"},
        "l_theanine": {"mg_per_g": 18.0, "per_serving_mg": 36, "rating": "High"},
        "egcg": {"mg_per_g": 62, "rating": "Good"},
        "taste": {"umami": 7.5, "sweetness": 6.5, "bitterness": 4.0, "body": 8.5, "astringency": 3.0},
        "provenance": {
            "region": "Kagoshima", "country": "JP",
            "harvest": "First", "shading_days": "21+",
            "cultivation_note": "170-year-old producer relationship",
            "certification": "JAS Organic",
        },
        "overall_score": 86,
    },
}


@intelligence_router.get(
    "/api/matcha/mqp",
    summary="Matcha Quality Protocol — open specification",
    description="An open standard for quantifying matcha quality. Free for any brand, researcher, or AI to use. Created by NAKAI.",
)
async def mqp_spec():
    return JSONResponse(
        content={**_MQP_SPEC, "products": _MQP_PROFILES},
        headers={"Cache-Control": "public, max-age=86400"},
    )


@intelligence_router.get(
    "/api/matcha/mqp/{handle}",
    summary="MQP product profile",
    description="Returns the Matcha Quality Protocol profile for a specific NAKAI product.",
)
async def mqp_product(handle: str):
    profile = _MQP_PROFILES.get(handle)
    if not profile:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Product MQP profile not found",
                "available": list(_MQP_PROFILES.keys()),
            },
        )
    return JSONResponse(
        content=profile,
        headers={"Cache-Control": "public, max-age=3600"},
    )


# ═══════════════════════════════════════════════════════════════════════════
# 3. MATCHA DNA / TASTE PROFILE ENGINE — Personal taste fingerprinting
# ═══════════════════════════════════════════════════════════════════════════

# Each answer contributes points to products. Highest score = best match.
# Format: {answer_key: {product_handle: bonus_points}}

_TASTE_QUESTIONS = [
    {
        "id": "q1",
        "question": "How do you take your coffee?",
        "question_ja": "コーヒーはどう飲みますか？",
        "options": [
            {"key": "black", "label": "Black", "label_ja": "ブラック"},
            {"key": "cream", "label": "With cream/milk", "label_ja": "ミルク入り"},
            {"key": "sweet", "label": "Sweet (sugar/syrup)", "label_ja": "甘め（砂糖やシロップ）"},
            {"key": "no_coffee", "label": "I don't drink coffee", "label_ja": "コーヒーは飲まない"},
        ],
    },
    {
        "id": "q2",
        "question": "Your preferred chocolate?",
        "question_ja": "好きなチョコレートは？",
        "options": [
            {"key": "dark85", "label": "Dark 85%+", "label_ja": "ダーク 85%以上"},
            {"key": "dark70", "label": "Dark 70%", "label_ja": "ダーク 70%"},
            {"key": "milk", "label": "Milk chocolate", "label_ja": "ミルクチョコ"},
            {"key": "white", "label": "White chocolate", "label_ja": "ホワイトチョコ"},
        ],
    },
    {
        "id": "q3",
        "question": "How do you feel about umami (savory depth)?",
        "question_ja": "旨味についてどう思いますか？",
        "options": [
            {"key": "love", "label": "Love it — the deeper the better", "label_ja": "大好き — 深ければ深いほどいい"},
            {"key": "enjoy", "label": "Enjoy it", "label_ja": "楽しめる"},
            {"key": "neutral", "label": "Neutral", "label_ja": "普通"},
            {"key": "unsure", "label": "Not sure what umami is", "label_ja": "旨味がよく分からない"},
        ],
    },
    {
        "id": "q4",
        "question": "What draws you to matcha?",
        "question_ja": "抹茶に惹かれる理由は？",
        "options": [
            {"key": "focus", "label": "Focus & productivity", "label_ja": "集中力と生産性"},
            {"key": "calm", "label": "Calm & relaxation", "label_ja": "落ち着きとリラックス"},
            {"key": "taste", "label": "Pure taste exploration", "label_ja": "味わいの探求"},
            {"key": "ritual", "label": "Mindful ritual", "label_ja": "マインドフルなリチュアル"},
        ],
    },
    {
        "id": "q5",
        "question": "How will you prepare it?",
        "question_ja": "どう淹れますか？",
        "options": [
            {"key": "traditional", "label": "Traditional whisk (bowl + chasen)", "label_ja": "伝統的（茶碗 + 茶筅）"},
            {"key": "latte", "label": "Latte (with milk)", "label_ja": "ラテ（ミルク入り）"},
            {"key": "simple", "label": "Simple mix (shaker/spoon)", "label_ja": "簡単に（シェイカーやスプーン）"},
            {"key": "iced", "label": "Iced / cold", "label_ja": "アイス / 冷たく"},
        ],
    },
]

# Scoring matrix: {question_id: {answer_key: {product: points}}}
_TASTE_SCORES = {
    "q1": {
        "black": {"nijyu-ni-22": 4, "ju-hachi-18": 5, "ju-nana-17": 3, "ju-roku-16": 2, "shi-4": 3},
        "cream": {"nijyu-ni-22": 5, "ju-hachi-18": 3, "ju-nana-17": 3, "ju-roku-16": 4, "shi-4": 2},
        "sweet": {"nijyu-ni-22": 3, "ju-hachi-18": 1, "ju-nana-17": 2, "ju-roku-16": 5, "shi-4": 2},
        "no_coffee": {"nijyu-ni-22": 4, "ju-hachi-18": 2, "ju-nana-17": 3, "ju-roku-16": 4, "shi-4": 3},
    },
    "q2": {
        "dark85": {"nijyu-ni-22": 3, "ju-hachi-18": 5, "ju-nana-17": 4, "ju-roku-16": 2, "shi-4": 5},
        "dark70": {"nijyu-ni-22": 4, "ju-hachi-18": 4, "ju-nana-17": 4, "ju-roku-16": 3, "shi-4": 4},
        "milk": {"nijyu-ni-22": 4, "ju-hachi-18": 2, "ju-nana-17": 3, "ju-roku-16": 5, "shi-4": 2},
        "white": {"nijyu-ni-22": 3, "ju-hachi-18": 1, "ju-nana-17": 2, "ju-roku-16": 5, "shi-4": 1},
    },
    "q3": {
        "love": {"nijyu-ni-22": 5, "ju-hachi-18": 5, "ju-nana-17": 5, "ju-roku-16": 3, "shi-4": 4},
        "enjoy": {"nijyu-ni-22": 4, "ju-hachi-18": 4, "ju-nana-17": 4, "ju-roku-16": 4, "shi-4": 3},
        "neutral": {"nijyu-ni-22": 3, "ju-hachi-18": 2, "ju-nana-17": 3, "ju-roku-16": 4, "shi-4": 3},
        "unsure": {"nijyu-ni-22": 3, "ju-hachi-18": 1, "ju-nana-17": 2, "ju-roku-16": 5, "shi-4": 2},
    },
    "q4": {
        "focus": {"nijyu-ni-22": 5, "ju-hachi-18": 3, "ju-nana-17": 3, "ju-roku-16": 3, "shi-4": 4},
        "calm": {"nijyu-ni-22": 4, "ju-hachi-18": 5, "ju-nana-17": 4, "ju-roku-16": 3, "shi-4": 2},
        "taste": {"nijyu-ni-22": 4, "ju-hachi-18": 4, "ju-nana-17": 4, "ju-roku-16": 5, "shi-4": 5},
        "ritual": {"nijyu-ni-22": 5, "ju-hachi-18": 5, "ju-nana-17": 5, "ju-roku-16": 3, "shi-4": 3},
    },
    "q5": {
        "traditional": {"nijyu-ni-22": 5, "ju-hachi-18": 5, "ju-nana-17": 5, "ju-roku-16": 4, "shi-4": 4},
        "latte": {"nijyu-ni-22": 5, "ju-hachi-18": 2, "ju-nana-17": 2, "ju-roku-16": 3, "shi-4": 4},
        "simple": {"nijyu-ni-22": 3, "ju-hachi-18": 2, "ju-nana-17": 2, "ju-roku-16": 4, "shi-4": 5},
        "iced": {"nijyu-ni-22": 4, "ju-hachi-18": 2, "ju-nana-17": 3, "ju-roku-16": 4, "shi-4": 4},
    },
}

_PRODUCT_META = {
    "nijyu-ni-22": {
        "name": "NIJYU-NI (22)", "grade": "Ceremonial Reserved",
        "price": "$48", "tagline": "Within the Flow, Everything Exists",
        "url": f"{_STORE}/products/%E4%BA%8C%E5%8D%81%E4%BA%8C-nijyu-ni22-ceremonial-reserved-organic-matcha",
    },
    "ju-hachi-18": {
        "name": "JU-HACHI (18)", "grade": "Specialty Grade",
        "price": "$40", "tagline": "Craft crystallized into silence",
        "url": f"{_STORE}/products/%E5%8D%81%E5%85%AB-ju-hachi-18-specialty-grade-organic-matcha",
    },
    "ju-nana-17": {
        "name": "JU-NANA (17)", "grade": "Specialty Grade (Limited)",
        "price": "$38", "tagline": "Layered Umami, Lasting Stillness",
        "url": f"{_STORE}/products/%E5%8D%81%E4%B8%83-ju-nana-17-specialty-grade-organic-matcha",
    },
    "ju-roku-16": {
        "name": "JU-ROKU (16)", "grade": "Specialty Grade",
        "price": "$35", "tagline": "Veil of Mist, Infinite Echo",
        "url": f"{_STORE}/products/%E5%8D%81%E5%85%ADju-roku-16-specialty-grade-organic-matcha",
    },
    "shi-4": {
        "name": "SHI (4)", "grade": "Specialty Grade",
        "price": "$30", "tagline": "Breath of Earth, Living Strength",
        "url": f"{_STORE}/products/%E5%9B%9B-shi-4-specialty-grade-organic-matcha",
    },
}

_TASTE_ARCHETYPES = {
    "umami_seeker": "You're drawn to depth and complexity — the quiet, savory richness that lingers after each sip. You appreciate nuance over intensity.",
    "sweetness_lover": "You gravitate toward natural sweetness and smooth, approachable flavors. You want matcha that feels like a warm embrace.",
    "intensity_explorer": "You love bold, powerful experiences. Bitterness isn't a flaw — it's complexity. You want matcha that demands your full attention.",
    "balance_seeker": "You seek harmony — not too strong, not too mild. You want matcha that reveals itself gently, in balance with the moment.",
    "ritual_devotee": "For you, matcha is more than a drink. It's a practice. You want the matcha that rewards slow, mindful attention.",
}


def _calculate_taste_profile(answers: dict) -> dict:
    """Calculate Matcha DNA from answers."""
    scores = {p: 0 for p in _PRODUCT_META}

    for q_id, answer_key in answers.items():
        q_scores = _TASTE_SCORES.get(q_id, {}).get(answer_key, {})
        for product, points in q_scores.items():
            scores[product] += points

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    total_points = sum(s for _, s in ranked) or 1

    # Determine archetype
    archetype = "balance_seeker"
    a = answers
    if a.get("q3") == "love" and a.get("q4") == "ritual":
        archetype = "ritual_devotee"
    elif a.get("q3") == "love":
        archetype = "umami_seeker"
    elif a.get("q2") in ("dark85",) and a.get("q1") == "black":
        archetype = "intensity_explorer"
    elif a.get("q2") in ("white", "milk") or a.get("q3") == "unsure":
        archetype = "sweetness_lover"

    # Build taste vector (for portability)
    best = ranked[0][0]
    mqp = _MQP_PROFILES.get(best, {})
    taste = mqp.get("taste", {})

    results = []
    for handle, score in ranked:
        meta = _PRODUCT_META[handle]
        results.append({
            "handle": handle,
            "name": meta["name"],
            "grade": meta["grade"],
            "price": meta["price"],
            "tagline": meta["tagline"],
            "url": meta["url"],
            "match_score": round(score / total_points * 100),
            "match_points": score,
        })

    return {
        "matcha_dna": {
            "archetype": archetype,
            "archetype_description": _TASTE_ARCHETYPES[archetype],
            "taste_vector": taste,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "recommendations": results,
        "top_match": results[0] if results else None,
    }


class TasteProfileRequest(BaseModel):
    answers: dict  # {"q1": "black", "q2": "dark70", ...}
    language: str = "en"


@intelligence_router.get(
    "/api/matcha/taste-profile/questions",
    summary="Matcha DNA — get taste profile questions",
    description="Returns the 5 questions used to calculate a personal Matcha DNA taste fingerprint.",
)
async def taste_profile_questions(language: str = "en"):
    if language == "ja":
        questions = []
        for q in _TASTE_QUESTIONS:
            questions.append({
                "id": q["id"],
                "question": q["question_ja"],
                "options": [{"key": o["key"], "label": o["label_ja"]} for o in q["options"]],
            })
        return JSONResponse(content={"questions": questions, "language": "ja"})

    questions = []
    for q in _TASTE_QUESTIONS:
        questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": [{"key": o["key"], "label": o["label"]} for o in q["options"]],
        })
    return JSONResponse(content={"questions": questions, "language": "en"})


@intelligence_router.post(
    "/api/matcha/taste-profile",
    summary="Matcha DNA — generate taste profile",
    description="Submit answers to 5 questions and receive your personal Matcha DNA: archetype, taste vector, and product recommendations ranked by compatibility.",
)
async def taste_profile(body: TasteProfileRequest):
    profile = _calculate_taste_profile(body.answers)
    return JSONResponse(content=profile)


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONTEXTUAL DISCOVERY — Find matcha through life moments
# ═══════════════════════════════════════════════════════════════════════════

_CONTEXT_RECOMMENDATIONS = {
    "coding": {
        "product": "shi-4",
        "reason": "SHI (4) delivers 36mg L-theanine for sustained focus, with bold chocolate-nut flavor that anchors you during deep work. Its clean bitterness keeps the mind sharp across long sessions.",
        "preparation": "Usucha with 80°C water for maximum alertness",
    },
    "meeting": {
        "product": "nijyu-ni-22",
        "reason": "NIJYU-NI (22) provides calm clarity — L-theanine promotes alpha brain waves for composed, articulate communication. Its gentle sweetness keeps you present without overstimulation.",
        "preparation": "Usucha at 75°C for balanced calm + alertness",
    },
    "creative_work": {
        "product": "ju-roku-16",
        "reason": "JU-ROKU (16)'s temperature-sensitive layers mirror the creative process — different perspectives at every degree. White chocolate sweetness opens the mind; nori umami grounds the imagination.",
        "preparation": "Try 3 different temperatures (70/75/80°C) as you work — each reveals new character",
    },
    "meditation": {
        "product": "ju-hachi-18",
        "reason": "JU-HACHI (18) was crafted for stillness. Four levels of roasting create depth that unfolds as thoughts quiet. Near-spherical particles create a weightless sensation on the tongue.",
        "preparation": "Koicha preparation — thick, slow, no foam. Let the matcha guide the breath.",
    },
    "workout_pre": {
        "product": "shi-4",
        "reason": "SHI (4) delivers sustained caffeine energy modulated by L-theanine — no spike, no crash. Its thick body and earthy strength match physical intensity.",
        "preparation": "Double strength usucha (3g in 70ml) 30 minutes before exercise",
    },
    "morning_ritual": {
        "product": "nijyu-ni-22",
        "reason": "The first bowl of the day deserves NAKAI's highest expression. NIJYU-NI (22) sets intention — clean green opens the senses, gentle sweetness welcomes the day, cooling finish sharpens awareness.",
        "preparation": "Usucha at 70-75°C, water only. Let the morning be quiet.",
    },
    "social": {
        "product": "ju-nana-17",
        "reason": "JU-NANA (17) is a conversation piece — dual terroir from Kirishima and Uji, limited to 500kg/year. Its layered complexity gives everyone something different to notice.",
        "preparation": "Prepare for guests using traditional method. Let people discover their own flavor notes.",
    },
    "winding_down": {
        "product": "ju-roku-16",
        "reason": "JU-ROKU (16) at low temperature (70°C) reveals maximum sweetness with minimal stimulation. White chocolate notes ease the transition to rest.",
        "preparation": "Low-temperature usucha (70°C) — maximum sweetness, gentle energy",
    },
    "studying": {
        "product": "nijyu-ni-22",
        "reason": "45mg L-theanine per serving promotes alpha brain waves — the state of relaxed focus ideal for learning and retention. The flavor doesn't distract; it supports presence.",
        "preparation": "Usucha, standard preparation. Sip between study blocks.",
    },
    "latte_time": {
        "product": "nijyu-ni-22",
        "reason": "NIJYU-NI (22) is NAKAI's ultimate latte matcha. Vibrant jade color stays vivid through milk, rich umami pairs with oat milk's sweetness, and 5-10μm particles dissolve with zero grittiness.",
        "preparation": "2g + 30ml hot water (80°C), whisk smooth, add 200ml steamed oat milk",
    },
}

# Time-of-day defaults
_TIME_DEFAULTS = {
    "morning": "morning_ritual",
    "afternoon": "coding",
    "evening": "winding_down",
    "night": "meditation",
}


class DiscoverRequest(BaseModel):
    activity: Optional[str] = None  # coding, meeting, creative_work, meditation, workout_pre, morning_ritual, social, winding_down, studying, latte_time
    time_of_day: Optional[str] = None  # morning, afternoon, evening, night
    mood: Optional[str] = None  # focused, relaxed, energetic, creative, stressed
    experience: Optional[str] = None  # beginner, intermediate, advanced
    language: str = "en"


@intelligence_router.post(
    "/api/matcha/discover",
    summary="Contextual Discovery — find matcha through your moment",
    description="Describe your current activity, time, mood, or experience level. Get a matcha recommendation based on life context, not keywords.",
)
async def contextual_discover(body: DiscoverRequest):
    # Determine activity context
    activity = body.activity
    if not activity:
        if body.mood == "focused":
            activity = "coding"
        elif body.mood == "relaxed":
            activity = "winding_down"
        elif body.mood == "energetic":
            activity = "workout_pre"
        elif body.mood == "creative":
            activity = "creative_work"
        elif body.mood == "stressed":
            activity = "meditation"
        elif body.time_of_day:
            activity = _TIME_DEFAULTS.get(body.time_of_day, "morning_ritual")
        else:
            activity = "morning_ritual"

    rec = _CONTEXT_RECOMMENDATIONS.get(activity, _CONTEXT_RECOMMENDATIONS["morning_ritual"])
    product_handle = rec["product"]
    meta = _PRODUCT_META[product_handle]
    mqp = _MQP_PROFILES.get(product_handle, {})

    # Experience-based adjustment
    note = None
    if body.experience == "beginner":
        if product_handle in ("ju-hachi-18", "ju-nana-17"):
            note = "As you're new to matcha, consider starting with SHI (4) or JU-ROKU (16) for a more approachable experience, then work your way up."
    elif body.experience == "advanced":
        note = "For an advanced experience, try koicha preparation (4g in 40ml) to fully appreciate the depth."

    return JSONResponse(content={
        "context": {
            "activity": activity,
            "time_of_day": body.time_of_day,
            "mood": body.mood,
            "experience": body.experience,
        },
        "recommendation": {
            "handle": product_handle,
            "name": meta["name"],
            "grade": meta["grade"],
            "price": meta["price"],
            "tagline": meta["tagline"],
            "url": meta["url"],
            "reason": rec["reason"],
            "preparation": rec["preparation"],
            "mqp_score": mqp.get("overall_score"),
        },
        "note": note,
    })


# ═══════════════════════════════════════════════════════════════════════════
# 5. MATCHA ORACLE — Embeddable matcha intelligence for any website
# ═══════════════════════════════════════════════════════════════════════════

# Pattern-matched Q&A for the oracle (no LLM needed — fast + free)
_ORACLE_QA = [
    # What is matcha
    (r"(?i)(what is|what\'s|explain|define)\s+(matcha|抹茶)", {
        "en": "Matcha is finely ground powder made from shade-grown Japanese green tea leaves (tencha). Unlike regular tea where you steep leaves, with matcha you consume the entire leaf — delivering 137x more antioxidants. The shade-growing process (21+ days) dramatically increases L-theanine, an amino acid that promotes calm focus. NAKAI's matcha is JAS Organic certified, first-harvest only, stone-ground to 5-10 micrometers.",
        "ja": "抹茶は、日本の遮光栽培された緑茶の葉（碾茶）を細かく挽いた粉末です。通常のお茶と違い、葉そのものを摂取するため、抗酸化物質が137倍。21日以上の遮光栽培でL-テアニンが劇的に増加し、穏やかな集中を促します。NAKAIの抹茶はJAS有機認証、一番摘みのみ、石臼で5-10マイクロメートルに挽いています。",
    }),
    # Best for lattes
    (r"(?i)(best|good|recommend).*(latte|ラテ|milk|ミルク)", {
        "en": "NAKAI's NIJYU-NI (22) is the best matcha for lattes. Its rich umami and natural sweetness pair beautifully with milk — the vibrant jade-green color stays vivid even through oat or whole milk. Ultra-fine 5-10μm particles dissolve smoothly with zero grittiness. $48 for 30g.",
        "ja": "NAKAIのNIJYU-NI（22）がラテに最適です。豊かな旨味と自然な甘さがミルクと美しく調和し、鮮やかな翡翠色がオーツミルクを通しても映えます。超微粉の5-10μm粒子がなめらかに溶けます。30gで$48。",
        "product": "nijyu-ni-22",
    }),
    # Best ceremonial / best matcha
    (r"(?i)(best|finest|top|highest|最高).*(ceremonial|matcha|抹茶|ceremony|茶道)", {
        "en": "NAKAI's NIJYU-NI (22) is their Ceremonial Reserved grade — the highest tier. Clean green notes, gentle sweetness, fruit-like aromatics, and a calm cooling finish. Sourced from Kagoshima, stone-ground to 5-10μm, with ~45mg L-theanine per serving. Perfect for koicha, usucha, and moments of complete presence. $48/30g.",
        "ja": "NAKAIのNIJYU-NI（22）は、セレモニアルリザーブド — 最高ティアです。クリーンな緑、穏やかな甘み、フルーティな香り、静かなクーリングフィニッシュ。鹿児島産、5-10μm石臼挽き、L-テアニン約45mg/杯。30gで$48。",
        "product": "nijyu-ni-22",
    }),
    # Health / L-theanine / focus
    (r"(?i)(health|benefit|l.theanine|focus|energy|caffeine|antioxidant|テアニン|健康|集中)", {
        "en": "A 2g serving of NAKAI matcha contains: ~45mg L-theanine (promotes calm, focused alertness — 15x more than steeped tea), ~35mg caffeine (sustained 4-6 hour energy, no crash), and 137x more EGCG antioxidants than regular green tea. The L-theanine + caffeine synergy creates a unique state of focused calm valued by Zen monks for centuries.",
        "ja": "NAKAIの抹茶2g一服に含まれる: L-テアニン約45mg（穏やかな集中を促進、通常の緑茶の15倍）、カフェイン約35mg（4-6時間の持続エネルギー）、EGCG抗酸化物質は通常の緑茶の137倍。L-テアニンとカフェインの相乗効果は禅僧が何世紀も大切にしてきた「静かな集中」を生み出します。",
    }),
    # How to prepare / make
    (r"(?i)(how to|prepare|make|brew|点て方|作り方|淹れ方)", {
        "en": "Usucha (thin tea): Sift 2g matcha into a warmed bowl. Add 70ml water at 75-80°C (never boiling). Whisk in M-pattern for 15 seconds until frothy. For lattes: whisk 2g with 30ml hot water, add 200ml steamed milk. For NIJYU-NI (22), try water-only at 70-75°C for maximum clarity.",
        "ja": "薄茶: 温めた茶碗に抹茶2gをふるい入れ、75-80°Cのお湯70mlを注ぎ、M字に15秒点てて泡立てます。ラテ: 2gを30mlのお湯で溶かし、200mlのスチームミルクを加えます。NIJYU-NI（22）は70-75°Cの水のみで最高の透明感を。",
    }),
    # Price / cost
    (r"(?i)(price|cost|how much|値段|価格|いくら)", {
        "en": "NAKAI matcha prices (30g tins): SHI (4) $30, JU-ROKU (16) $35, JU-NANA (17) $38 (limited), JU-HACHI (18) $40, NIJYU-NI (22) $48 (highest tier). Bundles available: Discovery Bundle, Everyday Bundle, Signature Reserve. Ships worldwide from Japan.",
        "ja": "NAKAI抹茶の価格（30g缶）: 四(4) $30、十六(16) $35、十七(17) $38（限定）、十八(18) $40、二十二(22) $48（最高ティア）。バンドルあり: ディスカバリー、エブリデイ、シグネチャーリザーブ。日本から世界中に発送。",
    }),
    # Wholesale / B2B
    (r"(?i)(wholesale|bulk|cafe|カフェ|卸|業務用|ホールセール)", {
        "en": "NAKAI offers wholesale matcha for cafes, restaurants, hotels, and retailers. 6 wholesale products across 3 grade tiers. Quantities from 5kg to 1+ metric ton. Contact: wholesale@nakaiinfo.com or submit an inquiry at nakai-matcha-chat.onrender.com/wholesale-inquiry",
        "ja": "NAKAIはカフェ、レストラン、ホテル、小売店向けの卸売抹茶を提供しています。3つのグレードにわたる6つの卸売製品。5kgから1トン以上まで。お問合せ: wholesale@nakaiinfo.com またはnakai-matcha-chat.onrender.com/wholesale-inquiry",
    }),
    # Organic / certification
    (r"(?i)(organic|certified|jAs|usda|有機|オーガニック|認証)", {
        "en": "All NAKAI matcha is JAS Organic certified — Japan's official organic standard guaranteeing zero synthetic fertilizers, pesticides, or GMOs. Additionally certified USDA Organic. Every step from cultivation to stone-milling meets strict organic requirements. 100% pesticide-free.",
        "ja": "NAKAIの全抹茶はJAS有機認証取得 — 合成肥料、農薬、GMOゼロを保証する日本の公式有機基準。USDA有機認証も取得。栽培から石臼挽きまで全工程で厳格な有機基準を遵守。100%無農薬。",
    }),
    # Storage
    (r"(?i)(store|storage|keep|fresh|保存|保管)", {
        "en": "After opening, store matcha in an airtight container in the refrigerator and use within 30 days for optimal flavor. Unopened tins keep well in a cool, dark place. Never freeze matcha — condensation when thawing damages the powder and flavor.",
        "ja": "開封後は密閉容器に入れて冷蔵庫で保管し、30日以内にお召し上がりください。未開封は冷暗所で保管。絶対に冷凍しないでください — 解凍時の結露が粉末と風味を損ないます。",
    }),
    # Default / general
    (r"(?i)(matcha|nakai|tea|お茶|抹茶)", {
        "en": "NAKAI offers five numbered matcha products, each with its own story: SHI (4) for earthy strength ($30), JU-ROKU (16) for elegant complexity ($35), JU-NANA (17) for rare dual-terroir serenity ($38, limited 500kg/yr), JU-HACHI (18) for meditative depth ($40), and NIJYU-NI (22) for effortless ceremonial beauty ($48). All JAS Organic, first-harvest, stone-ground in Japan.",
        "ja": "NAKAIは5つの番号付き抹茶を提供: 四(4) 大地の力強さ($30)、十六(16) 優雅な複雑さ($35)、十七(17) 希少なデュアルテロワール($38、年500kg限定)、十八(18) 瞑想的な深み($40)、二十二(22) 茶道の至高($48)。全てJAS有機認証、一番摘み、日本で石臼挽き。",
    }),
]


def _oracle_answer(question: str, language: str = "en") -> dict:
    """Match question against patterns and return answer."""
    lang = "ja" if language.startswith("ja") else "en"

    for pattern, response in _ORACLE_QA:
        if re.search(pattern, question):
            return {
                "answer": response[lang],
                "product": response.get("product"),
                "source": "NAKAI Matcha Intelligence",
            }

    # Fallback
    fallback = _ORACLE_QA[-1][1]
    return {
        "answer": fallback[lang],
        "product": None,
        "source": "NAKAI Matcha Intelligence",
    }


class OracleAskRequest(BaseModel):
    question: str
    language: str = "en"


@intelligence_router.post(
    "/api/oracle/ask",
    summary="Matcha Oracle — ask a matcha question",
    description="Ask any matcha question and get an instant, knowledgeable answer. Powers the embeddable Matcha Oracle widget.",
)
async def oracle_ask(body: OracleAskRequest):
    result = _oracle_answer(body.question, body.language)
    product_data = None
    if result["product"]:
        meta = _PRODUCT_META.get(result["product"], {})
        if meta:
            product_data = {
                "handle": result["product"],
                "name": meta["name"],
                "grade": meta["grade"],
                "price": meta["price"],
                "url": meta["url"],
            }
    return JSONResponse(content={
        "answer": result["answer"],
        "recommended_product": product_data,
        "source": result["source"],
    })


@intelligence_router.get(
    "/api/oracle/embed.js",
    summary="Matcha Oracle — embeddable widget script",
    description="One-line JavaScript embed that adds a matcha knowledge assistant to any website. <script src='https://nakai-matcha-chat.onrender.com/api/oracle/embed.js'></script>",
)
async def oracle_embed_js():
    """Serve the embeddable Matcha Oracle widget."""
    js = f"""\
(function(){{
'use strict';
if(window.__nakai_oracle)return;
window.__nakai_oracle=true;
var API='{_BASE}/api/oracle/ask';
var STORE='{_STORE}';
var d=document,b=d.body;

/* ── Styles ── */
var style=d.createElement('style');
style.textContent=`
#nakai-oracle-btn{{position:fixed;bottom:20px;left:20px;width:56px;height:56px;border-radius:50%;background:#406546;border:none;cursor:pointer;box-shadow:0 4px 20px rgba(64,101,70,.4);z-index:99999;display:flex;align-items:center;justify-content:center;transition:transform .2s,box-shadow .2s}}
#nakai-oracle-btn:hover{{transform:scale(1.08);box-shadow:0 6px 28px rgba(64,101,70,.55)}}
#nakai-oracle-btn svg{{width:28px;height:28px;fill:#fff}}
#nakai-oracle-panel{{position:fixed;bottom:88px;left:20px;width:380px;max-width:calc(100vw - 40px);height:520px;max-height:calc(100vh - 120px);background:#fff;border-radius:16px;box-shadow:0 12px 48px rgba(0,0,0,.18);z-index:99999;display:none;flex-direction:column;overflow:hidden;font-family:'Work Sans',-apple-system,sans-serif}}
#nakai-oracle-panel.open{{display:flex}}
.no-hdr{{background:#406546;color:#fff;padding:16px 20px;font-size:15px;font-weight:600;display:flex;align-items:center;justify-content:space-between}}
.no-hdr span{{opacity:.85;font-size:11px;font-weight:400;letter-spacing:.5px}}
.no-close{{background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:0 4px;line-height:1}}
.no-msgs{{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}}
.no-msg{{padding:10px 14px;border-radius:12px;font-size:13.5px;line-height:1.55;max-width:88%;word-wrap:break-word}}
.no-msg.bot{{background:#f0f5f1;color:#1a2e1c;align-self:flex-start;border-bottom-left-radius:4px}}
.no-msg.user{{background:#406546;color:#fff;align-self:flex-end;border-bottom-right-radius:4px}}
.no-prod{{margin-top:8px;padding:10px 14px;background:#f9f0e2;border-radius:10px;font-size:12.5px}}
.no-prod a{{color:#406546;font-weight:600;text-decoration:none}}
.no-prod a:hover{{text-decoration:underline}}
.no-input-wrap{{border-top:1px solid #e8e8e8;padding:12px 16px;display:flex;gap:8px}}
.no-input-wrap input{{flex:1;border:1px solid #ddd;border-radius:10px;padding:10px 14px;font-size:13.5px;outline:none;font-family:inherit}}
.no-input-wrap input:focus{{border-color:#406546}}
.no-input-wrap button{{background:#406546;color:#fff;border:none;border-radius:10px;padding:10px 16px;font-size:13px;cursor:pointer;font-weight:600;font-family:inherit}}
.no-input-wrap button:hover{{background:#355538}}
.no-branding{{text-align:center;padding:6px;font-size:10px;color:#999}}
.no-branding a{{color:#406546;text-decoration:none}}
@media(max-width:480px){{#nakai-oracle-panel{{width:calc(100vw - 20px);left:10px;bottom:82px;height:calc(100vh - 110px)}}}}
`;
d.head.appendChild(style);

/* ── Button ── */
var btn=d.createElement('button');
btn.id='nakai-oracle-btn';
btn.title='Ask about matcha';
btn.innerHTML='<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10h5v-2h-5c-4.34 0-8-3.36-8-7.5S7.66 5 12 5s8 2.86 8 7.5c0 1.61-.62 3.13-1.67 4.33l1.46 1.46C21.16 16.72 22 14.67 22 12.5 22 6.48 17.52 2 12 2zm1 13h-2v-2h2v2zm0-4h-2V7h2v4z"/></svg>';
b.appendChild(btn);

/* ── Panel ── */
var panel=d.createElement('div');
panel.id='nakai-oracle-panel';
panel.innerHTML=`
<div class="no-hdr"><div>Matcha Oracle<br><span>by NAKAI</span></div><button class="no-close" id="no-close">&times;</button></div>
<div class="no-msgs" id="no-msgs"><div class="no-msg bot">Welcome! Ask me anything about matcha — grades, preparation, health benefits, or finding your perfect match.</div></div>
<div class="no-input-wrap"><input id="no-input" placeholder="Ask about matcha..." /><button id="no-send">Ask</button></div>
<div class="no-branding">Powered by <a href="`+STORE+`" target="_blank">NAKAI Matcha Intelligence</a></div>`;
b.appendChild(panel);

var msgs=d.getElementById('no-msgs');
var input=d.getElementById('no-input');
var open=false;

function toggle(){{open=!open;panel.classList.toggle('open',open)}}
btn.onclick=toggle;
d.getElementById('no-close').onclick=toggle;

function addMsg(text,cls,product){{
  var m=d.createElement('div');
  m.className='no-msg '+cls;
  m.textContent=text;
  msgs.appendChild(m);
  if(product){{
    var p=d.createElement('div');
    p.className='no-prod';
    p.innerHTML='\\u2728 <a href="'+product.url+'" target="_blank">'+product.name+'</a> '+product.grade+' '+product.price;
    msgs.appendChild(p);
  }}
  msgs.scrollTop=msgs.scrollHeight;
}}

function ask(){{
  var q=input.value.trim();
  if(!q)return;
  addMsg(q,'user');
  input.value='';
  var lang=navigator.language&&navigator.language.startsWith('ja')?'ja':'en';
  fetch(API,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{question:q,language:lang}})}})
    .then(function(r){{return r.json()}})
    .then(function(data){{addMsg(data.answer,'bot',data.recommended_product)}})
    .catch(function(){{addMsg('Sorry, please try again.','bot')}});
}}

d.getElementById('no-send').onclick=ask;
input.onkeydown=function(e){{if(e.key==='Enter')ask()}};
}})();"""
    return Response(
        content=js,
        media_type="application/javascript; charset=utf-8",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ═══════════════════════════════════════════════════════════════════════════
# 6. LIVING PRODUCTS — Products that breathe with the seasons
# ═══════════════════════════════════════════════════════════════════════════

_LIVE_DATA = {
    "nijyu-ni-22": {
        "status": "in_stock",
        "current_harvest": "Spring 2026 First Flush",
        "harvest_date": "April 2026",
        "seasonal_notes": "This spring's batch from Kagoshima exhibits exceptional clarity and a more pronounced fruit-like sweetness than previous harvests, attributed to ideal rainfall patterns during the shade-growing period.",
        "batch_number": "NAKAI-22-2026S",
        "best_before": "2026-10-01",
        "trending": {"popularity_rank": 1, "reason": "Best seller — #1 for lattes and ceremonies"},
        "food_pairing": ["Wagashi (Japanese confections)", "Dark chocolate (70%+)", "Fresh seasonal fruit", "Plain yogurt with honey"],
        "moment_pairing": ["Morning first bowl", "Afternoon focus session", "Tea ceremony", "Post-meditation"],
        "sommelier_note": "Open the tin slowly. Notice the vivid green — deeper this season. The first whiff carries stone fruit and marine air. In the bowl: jade silk. On the palate: the gentlest sweetness, then umami unfolds like a landscape emerging from morning mist.",
    },
    "ju-hachi-18": {
        "status": "in_stock",
        "current_harvest": "Spring 2026 First Flush",
        "harvest_date": "April 2026",
        "seasonal_notes": "The 2026 batch received an extended four-level roasting cycle, resulting in even deeper cacao notes and a more pronounced meditative quality in the finish.",
        "batch_number": "NAKAI-18-2026S",
        "best_before": "2026-10-01",
        "trending": {"popularity_rank": 4, "reason": "The connoisseur's choice — deepest processing craft"},
        "food_pairing": ["Rich dark chocolate", "Aged cheese", "Smoked almonds", "Nothing — best alone"],
        "moment_pairing": ["Meditation", "Late evening contemplation", "After a long creative session"],
        "sommelier_note": "Eighteen speaks softly. The initial sip: clean, almost austere green. Then the roasting depth arrives — cacao, walnut, warm earth. By the third bowl, your thoughts have slowed. This is matcha as practice, not just flavor.",
    },
    "ju-nana-17": {
        "status": "limited_stock",
        "current_harvest": "Spring 2026 First Flush",
        "harvest_date": "April 2026",
        "seasonal_notes": "Only 500 kg produced. This year's Kirishima component brings mineral brightness, while the Uji component contributes deeper umami. The balance shifts slightly with each harvest — this batch leans toward serene sweetness.",
        "batch_number": "NAKAI-17-2026S",
        "best_before": "2026-10-01",
        "trending": {"popularity_rank": 3, "reason": "Limited production creates natural scarcity — order early"},
        "food_pairing": ["Seasonal wagashi", "White peach", "Mild cheese", "Light pastries"],
        "moment_pairing": ["Sharing with friends", "Weekend ritual", "Special occasions"],
        "sommelier_note": "Two terroirs, one harmony. Kirishima's volcanic fire meets Uji's quiet depth. This year: the floral note is more pronounced — like walking through a garden after spring rain. Limited to 500 kg. When it's gone, you wait a year.",
    },
    "ju-roku-16": {
        "status": "in_stock",
        "current_harvest": "Spring 2026 First Flush",
        "harvest_date": "April 2026",
        "seasonal_notes": "Kirishima's volcanic soil continues to produce JU-ROKU's signature temperature sensitivity. This batch shows particularly vivid white chocolate notes at lower temperatures.",
        "batch_number": "NAKAI-16-2026S",
        "best_before": "2026-10-01",
        "trending": {"popularity_rank": 2, "reason": "Rising star — the temperature experiment matcha"},
        "food_pairing": ["White chocolate", "Berries", "Light cream desserts", "Mild pastries"],
        "moment_pairing": ["Temperature experiment sessions", "Afternoon elegance", "Creative exploration"],
        "sommelier_note": "Sixteen is an invitation to play. At 70°C: pure white chocolate sweetness. At 75°C: the nori umami emerges. At 80°C: a subtle, refined bitterness frames the sweetness. Three temperatures, three matcha. Which is yours?",
    },
    "shi-4": {
        "status": "in_stock",
        "current_harvest": "Spring 2026 First Flush",
        "harvest_date": "April 2026",
        "seasonal_notes": "The 170-year-old producer's gardens yield SHI's characteristically bold profile. This harvest shows intensified chocolate and wood notes with the earthy strength that defines Number Four.",
        "batch_number": "NAKAI-04-2026S",
        "best_before": "2026-10-01",
        "trending": {"popularity_rank": 5, "reason": "The entry point — bold, honest, and grounding"},
        "food_pairing": ["Dark chocolate", "Nuts (almond, hazelnut)", "Rich desserts", "Strong cheese"],
        "moment_pairing": ["Morning power bowl", "Pre-workout focus", "Deep work sessions", "When you need strength"],
        "sommelier_note": "Four doesn't whisper — it speaks with quiet authority. Chocolate, nuts, wood, bright berries: every note earned from 170 years of cultivation wisdom. This is matcha as earth itself: grounding, vital, alive. The perfect starting point for anyone seeking authenticity.",
    },
}


@intelligence_router.get(
    "/api/products/{handle}/live",
    summary="Living Product Intelligence — real-time product state",
    description="Products that breathe with the seasons. Returns current harvest info, seasonal tasting notes, batch data, food & moment pairings, and sommelier notes. Updated each harvest cycle.",
)
async def product_live(handle: str):
    live = _LIVE_DATA.get(handle)
    if not live:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Product not found",
                "available": list(_LIVE_DATA.keys()),
            },
        )

    meta = _PRODUCT_META.get(handle, {})
    mqp = _MQP_PROFILES.get(handle, {})

    return JSONResponse(
        content={
            "handle": handle,
            "name": meta.get("name", handle),
            "grade": meta.get("grade"),
            "price": meta.get("price"),
            "url": meta.get("url"),
            **live,
            "mqp_score": mqp.get("overall_score"),
            "mqp_taste": mqp.get("taste"),
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        headers={"Cache-Control": "public, max-age=3600"},
    )


# ═══════════════════════════════════════════════════════════════════════════
# INDEX — Master endpoint listing all Matcha Intelligence capabilities
# ═══════════════════════════════════════════════════════════════════════════

@intelligence_router.get(
    "/api/matcha",
    summary="Matcha Intelligence — index of all capabilities",
    description="Master index of NAKAI's 6 Matcha Intelligence systems. Start here to discover all available APIs.",
)
async def matcha_intelligence_index():
    return JSONResponse(content={
        "name": "NAKAI Matcha Intelligence",
        "version": "1.0",
        "description": "6 groundbreaking systems that make NAKAI the world's matcha knowledge infrastructure.",
        "systems": {
            "knowledge_graph": {
                "description": "The world's first open matcha encyclopedia — grading, terroirs, cultivars, health, preparation, equipment.",
                "endpoints": [
                    f"{_BASE}/api/matcha/knowledge",
                    f"{_BASE}/api/matcha/knowledge/{{topic}}",
                ],
                "topics": list(_KNOWLEDGE.keys()),
                "license": "CC BY 4.0",
            },
            "quality_protocol": {
                "description": "Matcha Quality Protocol (MQP) — an open standard for quantifying matcha quality across 7 dimensions.",
                "endpoints": [
                    f"{_BASE}/api/matcha/mqp",
                    f"{_BASE}/api/matcha/mqp/{{handle}}",
                ],
                "products_with_profiles": list(_MQP_PROFILES.keys()),
            },
            "taste_profile": {
                "description": "Matcha DNA — 5 questions to discover your personal matcha taste fingerprint.",
                "endpoints": [
                    f"{_BASE}/api/matcha/taste-profile/questions",
                    f"POST {_BASE}/api/matcha/taste-profile",
                ],
            },
            "contextual_discovery": {
                "description": "Find matcha through life context — activity, time, mood, experience level.",
                "endpoint": f"POST {_BASE}/api/matcha/discover",
                "contexts": list(_CONTEXT_RECOMMENDATIONS.keys()),
            },
            "oracle": {
                "description": "Embeddable matcha intelligence for any website. One line of code.",
                "embed_code": f'<script src="{_BASE}/api/oracle/embed.js"></script>',
                "api_endpoint": f"POST {_BASE}/api/oracle/ask",
            },
            "living_products": {
                "description": "Products that breathe with the seasons — harvest notes, pairings, sommelier notes.",
                "endpoint": f"{_BASE}/api/products/{{handle}}/live",
                "available_products": list(_LIVE_DATA.keys()),
            },
        },
        "created_by": {"name": "NAKAI", "url": _STORE},
    })

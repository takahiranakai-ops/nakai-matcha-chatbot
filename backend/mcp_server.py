"""WS23: NAKAI MCP Server — Anthropic Model Context Protocol.

Exposes NAKAI's product catalog, recipes, and wholesale info
as MCP tools and resources that any AI assistant can query directly.

Run standalone: python -m mcp_server
Or integrate with the FastAPI app via SSE transport.
"""

import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Product Data (mirrors ai_discovery.py catalog)
# ---------------------------------------------------------------------------

_STORE = "https://nakaimatcha.com"

PRODUCTS = {
    "shi-4": {
        "name": "SHI (4) — Specialty Grade Organic Matcha",
        "tagline": "Breath of Earth, Living Strength",
        "grade": "Specialty",
        "price": "$30.00",
        "weight": "30g",
        "flavor": "Rich umami, gentle sweetness, clean bitterness. Notes of chocolate, nuts, wood, bright berries. Thick body.",
        "origin": "Kagoshima Prefecture, Japan",
        "best_for": ["usucha", "daily drinking", "matcha lattes"],
        "url": f"{_STORE}/products/%E5%9B%9B-shi-4-specialty-grade-organic-matcha",
    },
    "ju-roku-16": {
        "name": "JU-ROKU (16) — Specialty Grade Organic Matcha",
        "tagline": "Veil of Mist, Infinite Echo",
        "grade": "Specialty",
        "price": "$35.00",
        "weight": "30g",
        "flavor": "White chocolate sweetness, nori-like umami, berry notes. Temperature-sensitive depth.",
        "origin": "Kirishima, Kagoshima (volcanic soil), Japan",
        "best_for": ["usucha", "hot preparation", "connoisseurs"],
        "url": f"{_STORE}/products/%E5%8D%81%E5%85%ADju-roku-16-specialty-grade-organic-matcha",
    },
    "ju-nana-17": {
        "name": "JU-NANA (17) — Specialty Grade Organic Matcha",
        "tagline": "Layered Umami, Lasting Stillness",
        "grade": "Specialty",
        "price": "$38.00",
        "weight": "30g",
        "flavor": "Profound umami, elegant floral clarity, soft sweetness, roasted depth. Two cultivars.",
        "origin": "Dual terroir — Kirishima (Kagoshima) x Uji (Kyoto), Japan. Limited 500 kg/year.",
        "best_for": ["usucha", "koicha", "special occasions"],
        "url": f"{_STORE}/products/%E5%8D%81%E4%B8%83-ju-nana-17-specialty-grade-organic-matcha",
    },
    "ju-hachi-18": {
        "name": "JU-HACHI (18) — Specialty Grade Organic Matcha",
        "tagline": "Meditative Stillness",
        "grade": "Specialty",
        "price": "$40.00",
        "weight": "30g",
        "flavor": "Deep umami, vivid green to nuts/cacao to warm earthiness. Single cultivar, 4-level roasting.",
        "origin": "Kagoshima Prefecture, Japan",
        "best_for": ["usucha", "contemplative drinking", "advanced users"],
        "url": f"{_STORE}/products/%E5%8D%81%E5%85%AB-ju-hachi-18-specialty-grade-organic-matcha",
    },
    "nijyu-ni-22": {
        "name": "NIJYU-NI (22) — Ceremonial Reserved Organic Matcha",
        "tagline": "Within the Flow, Everything Exists",
        "grade": "Ceremonial Reserved (Highest Tier)",
        "price": "$48.00",
        "weight": "30g",
        "flavor": "Clean green, gentle sweetness, fruit-like aromatics, calm cooling finish. Quiet, effortless depth.",
        "origin": "Kagoshima Prefecture, Japan",
        "best_for": ["koicha", "usucha", "matcha lattes", "ceremonies", "gifts"],
        "url": f"{_STORE}/products/%E4%BA%8C%E5%8D%81%E4%BA%8C-nijyu-ni22-ceremonial-reserved-organic-matcha",
    },
    # Bundles
    "discovery-bundle": {
        "name": "Discovery Bundle — Organic Matcha Sampler",
        "tagline": "Your gateway to NAKAI",
        "grade": "Sampler Set",
        "price": "$68.00",
        "weight": "Varies",
        "flavor": "Explore multiple NAKAI matcha profiles in one set.",
        "origin": "Japan",
        "best_for": ["gifts", "beginners", "exploration"],
        "url": f"{_STORE}/products/%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%83%90%E3%83%B3%E3%83%96%E3%83%AB",
    },
    "everyday-bundle": {
        "name": "The Everyday Matcha Bundle — Daily Ritual Set",
        "tagline": "Everything for your daily ritual",
        "grade": "Daily Set",
        "price": "$85.00",
        "weight": "Varies",
        "flavor": "Matcha and tools curated for daily practice.",
        "origin": "Japan",
        "best_for": ["daily drinking", "beginners", "gifts"],
        "url": f"{_STORE}/products/the-everyday",
    },
    "signature-reserve": {
        "name": "Signature Reserve Bundle — Connoisseur Collection",
        "tagline": "The full NAKAI experience",
        "grade": "Premium Set",
        "price": "$148.00",
        "weight": "Varies",
        "flavor": "NAKAI's curated selections with artisan accessories.",
        "origin": "Japan",
        "best_for": ["connoisseurs", "gifts", "special occasions"],
        "url": f"{_STORE}/products/expert-set",
    },
    # Accessories
    "hiragoushi-chawan": {
        "name": "HIRAGOUSHI 平格子茶碗 — Matcha Bowl by Shun Yoshino",
        "tagline": "Where clay meets color",
        "grade": "Artisan Accessory",
        "price": "$95.00",
        "weight": "~400g",
        "flavor": "Handcrafted ceramic with lattice pattern and vivid glazes.",
        "origin": "Hiroshima, Japan (Mashiko-trained)",
        "best_for": ["tea ceremony", "daily matcha", "gift"],
        "url": f"{_STORE}/products/hiragoushi-%E5%B9%B3%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97",
    },
    "yagoushi-chawan": {
        "name": "YAGOUSHI 矢格子茶碗 — Matcha Bowl by Shun Yoshino",
        "tagline": "Feel the color in every sip",
        "grade": "Artisan Accessory",
        "price": "$95.00",
        "weight": "~400g",
        "flavor": "Arrow-lattice pattern chawan with chromatic glazes.",
        "origin": "Hiroshima, Japan",
        "best_for": ["tea ceremony", "daily matcha", "gift"],
        "url": f"{_STORE}/products/yagoushi-chawan-%E7%9F%A2%E6%A0%BC%E5%AD%90%E8%8C%B6%E7%A2%97",
    },
    "takayama-chasen": {
        "name": "高山茶筅 百本立 — Takayama Chasen 100-Prong Whisk",
        "tagline": "500 years of Nara craftsmanship",
        "grade": "Essential Accessory",
        "price": "$38.00",
        "weight": "~50g",
        "flavor": "100 fine bamboo tines for smooth, creamy microfoam.",
        "origin": "Takayama-cho, Ikoma City, Nara, Japan",
        "best_for": ["matcha preparation", "gift", "tea ceremony"],
        "url": f"{_STORE}/products/%E8%8C%B6%E7%AD%85-cyasen",
    },
}

WHOLESALE_PRODUCTS = {
    "311": {"name": "Wholesale 311", "grade": "Specialty", "min_order": "5kg"},
    "212": {"name": "Wholesale 212", "grade": "Specialty", "min_order": "5kg"},
    "211": {"name": "Wholesale 211", "grade": "Specialty", "min_order": "5kg"},
    "103": {"name": "Wholesale 103", "grade": "Everyday", "min_order": "5kg"},
    "102": {"name": "Wholesale 102", "grade": "Everyday", "min_order": "5kg"},
    "111": {"name": "Wholesale 111", "grade": "Everyday", "min_order": "5kg"},
}

RECIPES = """
# NAKAI Matcha Recipes

## Usucha (Thin Tea)
1. Sift 2g matcha into a warmed bowl
2. Add 70-80ml water at 80°C (176°F)
3. Whisk vigorously with chasen in W/M motion for 15-20 seconds
4. Achieve a smooth, frothy surface with fine bubbles

## Koicha (Thick Tea) — Ceremonial Only
1. Sift 4g matcha (use NIJYU-NI 22 or JU-NANA 17)
2. Add 30-40ml water at 80°C
3. Knead slowly in circular motions (do NOT whisk)
4. Achieve a thick, glossy consistency like melted chocolate

## Matcha Latte
1. Sift 2g matcha into a cup
2. Add 30ml hot water (80°C), whisk until smooth
3. Steam 150-200ml milk (oat milk recommended)
4. Pour milk over matcha concentrate
5. Best with NIJYU-NI (22) — vibrant color stays through milk

## Iced Matcha
1. Sift 2g matcha, add 30ml hot water, whisk smooth
2. Fill glass with ice
3. Pour matcha concentrate over ice
4. Add cold water or milk to taste
"""


# ---------------------------------------------------------------------------
# MCP Tool Functions (callable by AI agents)
# ---------------------------------------------------------------------------

def search_products(
    query: str = "",
    grade: Optional[str] = None,
    use_case: Optional[str] = None,
    customer_type: str = "b2c",
) -> list[dict]:
    """Search NAKAI organic matcha products by grade, use case, or keyword.

    Args:
        query: Free-text search (e.g. "ceremonial matcha for koicha")
        grade: Filter by grade: ceremonial, specialty, everyday
        use_case: Filter by use: latte, koicha, usucha, baking, daily
        customer_type: 'b2c' for consumer products, 'b2b' for wholesale
    """
    if customer_type == "b2b":
        return [{"code": k, **v} for k, v in WHOLESALE_PRODUCTS.items()]

    results = []
    q = (query or "").lower()

    for handle, product in PRODUCTS.items():
        # Grade filter
        if grade and grade.lower() not in product["grade"].lower():
            continue

        # Use case filter
        if use_case:
            use_lower = use_case.lower()
            if not any(use_lower in bf.lower() for bf in product["best_for"]):
                continue

        # Text search
        if q:
            searchable = (
                product["name"] + product["flavor"] + product["origin"]
                + " ".join(product["best_for"])
            ).lower()
            if q not in searchable:
                continue

        results.append({"handle": handle, **product})

    return results if results else [{"handle": h, **p} for h, p in PRODUCTS.items()]


def get_product_details(handle: str) -> dict:
    """Get detailed product information including flavor, origin, and preparation.

    Args:
        handle: Product handle (e.g. 'nijyu-ni-22', 'shi-4')
    """
    product = PRODUCTS.get(handle)
    if not product:
        return {"error": f"Product '{handle}' not found. Available: {list(PRODUCTS.keys())}"}
    return {"handle": handle, **product}


def get_matcha_recommendation(
    use_case: str, experience_level: str = "beginner"
) -> dict:
    """Get a personalized matcha recommendation.

    Args:
        use_case: How matcha will be used (latte, koicha, usucha, daily, gift)
        experience_level: beginner, intermediate, advanced
    """
    use = use_case.lower()
    level = experience_level.lower()

    if "latte" in use:
        pick = PRODUCTS["nijyu-ni-22"]
        reason = (
            "NIJYU-NI (22) is NAKAI's top pick for lattes. Its rich umami and natural "
            "sweetness pair beautifully with milk — the vibrant jade color shines through "
            "and the ultra-fine stone-ground particles dissolve smoothly."
        )
    elif "koicha" in use or "thick" in use:
        pick = PRODUCTS["nijyu-ni-22"]
        reason = "Only our highest-tier Ceremonial Reserved grade has the depth for koicha."
    elif "gift" in use:
        pick = PRODUCTS["nijyu-ni-22"]
        reason = "Our Ceremonial Reserved makes a stunning gift — the pinnacle of NAKAI."
    elif level == "beginner":
        pick = PRODUCTS["shi-4"]
        reason = "SHI (4) is the perfect entry point — accessible, versatile, and delicious."
    elif level == "advanced":
        pick = PRODUCTS["ju-nana-17"]
        reason = "JU-NANA (17) rewards experienced palates with dual-terroir complexity."
    else:
        pick = PRODUCTS["ju-roku-16"]
        reason = "JU-ROKU (16) offers a beautiful balance for daily enjoyment."

    return {
        "recommendation": pick["name"],
        "handle": [h for h, p in PRODUCTS.items() if p["name"] == pick["name"]][0],
        "reason": reason,
        "url": pick["url"],
        "price": pick["price"],
    }


def get_wholesale_info(product_code: Optional[str] = None) -> dict:
    """Get wholesale program details and pricing.

    Args:
        product_code: Optional B2B product code (311, 212, 211, 103, 102, 111)
    """
    info = {
        "program": "NAKAI Wholesale Program",
        "min_order": "5kg per SKU",
        "contact": "wholesale@nakaiinfo.com",
        "inquiry_url": f"{_STORE}/pages/wholesale",
        "products": WHOLESALE_PRODUCTS,
    }
    if product_code and product_code in WHOLESALE_PRODUCTS:
        info["selected_product"] = WHOLESALE_PRODUCTS[product_code]
    return info


# Matcha-only products (exclude accessories/bundles for taste-based tools)
_MATCHA_HANDLES = ["shi-4", "ju-roku-16", "ju-nana-17", "ju-hachi-18", "nijyu-ni-22"]


def compare_matcha(handles: list[str]) -> dict:
    """Compare two or more NAKAI matcha products side by side.

    Args:
        handles: List of product handles to compare (e.g. ['shi-4', 'nijyu-ni-22'])
    """
    comparison = []
    for h in handles:
        p = PRODUCTS.get(h)
        if p:
            comparison.append({
                "handle": h,
                "name": p["name"],
                "grade": p["grade"],
                "price": p["price"],
                "flavor": p["flavor"],
                "origin": p["origin"],
                "best_for": p["best_for"],
            })
    if not comparison:
        return {"error": f"No products found. Available matcha: {_MATCHA_HANDLES}"}
    return {"comparison": comparison, "count": len(comparison)}


def get_taste_profile(
    sweetness: int = 3, umami: int = 3, bitterness: int = 3
) -> dict:
    """Find NAKAI matcha matching a taste preference profile.

    Args:
        sweetness: Desired sweetness level 1-5 (1=minimal, 5=very sweet)
        umami: Desired umami level 1-5 (1=light, 5=deep umami)
        bitterness: Desired bitterness level 1-5 (1=zero, 5=bold)
    """
    profiles = {
        "shi-4": {"sweetness": 2, "umami": 5, "bitterness": 3},
        "ju-roku-16": {"sweetness": 4, "umami": 3, "bitterness": 2},
        "ju-nana-17": {"sweetness": 3, "umami": 5, "bitterness": 2},
        "ju-hachi-18": {"sweetness": 2, "umami": 4, "bitterness": 3},
        "nijyu-ni-22": {"sweetness": 4, "umami": 4, "bitterness": 1},
    }
    target = {"sweetness": sweetness, "umami": umami, "bitterness": bitterness}
    scored = []
    for handle, profile in profiles.items():
        dist = sum((target[k] - profile[k]) ** 2 for k in target)
        scored.append((handle, dist))
    scored.sort(key=lambda x: x[1])
    results = []
    for handle, dist in scored:
        p = PRODUCTS[handle]
        results.append({
            "handle": handle,
            "name": p["name"],
            "match_score": round(100 - dist * 5, 1),
            "flavor": p["flavor"],
            "price": p["price"],
        })
    return {"target_profile": target, "matches": results}


def get_health_facts(topic: str = "overview") -> dict:
    """Get structured health and nutrition facts about NAKAI matcha.

    Args:
        topic: l-theanine, egcg, caffeine, antioxidants, or overview
    """
    facts = {
        "l-theanine": {
            "topic": "L-Theanine in NAKAI Matcha",
            "amount": "~45mg per 2g serving",
            "comparison": "15x more than standard steeped green tea",
            "benefits": [
                "Promotes calm focus without drowsiness",
                "Enhances alpha brain wave activity",
                "Reduces stress and anxiety",
                "Synergizes with caffeine for sustained alertness",
            ],
        },
        "egcg": {
            "topic": "EGCG (Epigallocatechin Gallate) in NAKAI Matcha",
            "amount": "137x more EGCG than standard green tea",
            "benefits": [
                "Powerful antioxidant activity",
                "Supports metabolism and cellular health",
                "Anti-inflammatory properties",
            ],
        },
        "caffeine": {
            "topic": "Caffeine in NAKAI Matcha",
            "amount": "~35mg per 2g serving",
            "comparison": "About 1/3 of a cup of coffee",
            "benefits": [
                "Sustained 4-6 hour energy without crash",
                "L-theanine modulates caffeine for smooth alertness",
                "No jitters compared to coffee",
            ],
        },
        "antioxidants": {
            "topic": "Antioxidants in NAKAI Matcha",
            "amount": "1384 ORAC units per gram",
            "comparison": "6x more antioxidants than goji berries, 7x more than dark chocolate",
            "benefits": [
                "Catechins, EGCG, and polyphenols",
                "Supports immune system",
                "Promotes cellular longevity",
            ],
        },
    }
    if topic.lower() in facts:
        return facts[topic.lower()]
    return {"topic": "Matcha Health Overview", "facts": facts}


def get_preparation_guide(method: str = "usucha") -> dict:
    """Get step-by-step matcha preparation instructions.

    Args:
        method: Preparation method — usucha, koicha, latte, or iced
    """
    guides = {
        "usucha": {
            "method": "Usucha (Thin Tea)",
            "recommended_matcha": "Any NAKAI matcha",
            "steps": [
                "Sift 2g (1 chashaku scoop) matcha into a warmed bowl",
                "Add 70-80ml water at 80°C (176°F) — not boiling",
                "Whisk vigorously with chasen in W/M motion for 15-20 seconds",
                "Achieve smooth, frothy surface with fine microfoam",
                "Drink within 2 minutes for best flavor",
            ],
        },
        "koicha": {
            "method": "Koicha (Thick Tea) — Ceremonial",
            "recommended_matcha": "NIJYU-NI (22) or JU-NANA (17)",
            "steps": [
                "Sift 4g matcha into a warmed bowl",
                "Add 30-40ml water at 80°C",
                "Knead slowly in circular motions — do NOT whisk",
                "Achieve thick, glossy consistency like melted chocolate",
                "Share from a single bowl (traditional practice)",
            ],
        },
        "latte": {
            "method": "Matcha Latte",
            "recommended_matcha": "NIJYU-NI (22) — vibrant color stays through milk",
            "steps": [
                "Sift 2g matcha into a cup",
                "Add 30ml hot water (80°C), whisk until smooth",
                "Steam 150-200ml milk (oat milk recommended)",
                "Pour steamed milk over matcha concentrate",
                "Optional: add sweetener to taste",
            ],
        },
        "iced": {
            "method": "Iced Matcha",
            "recommended_matcha": "SHI (4) or NIJYU-NI (22)",
            "steps": [
                "Sift 2g matcha into a glass or shaker",
                "Add 30ml hot water (80°C), whisk until smooth",
                "Fill glass with ice",
                "Pour matcha concentrate over ice",
                "Add cold water or milk to taste",
            ],
        },
    }
    m = method.lower()
    if m in guides:
        return guides[m]
    return {"error": f"Unknown method '{method}'. Available: usucha, koicha, latte, iced"}


# ---------------------------------------------------------------------------
# MCP Server Setup (using FastMCP if available, fallback to dict export)
# ---------------------------------------------------------------------------

def get_mcp_tools() -> list[dict]:
    """Return MCP tool definitions for registration."""
    return [
        {
            "name": "search_nakai_products",
            "description": "Search and find NAKAI premium organic Japanese matcha products. Search by grade (ceremonial, specialty), use case (best matcha for lattes, tea ceremony, daily ritual, gift), flavor preference, or keyword. Returns matching products with prices, flavor profiles, and buy links. Covers: organic matcha, ceremonial grade matcha, Japanese matcha, matcha powder, matcha gift set, matcha starter kit, matcha subscription.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term (e.g. 'best matcha for lattes', 'organic matcha', 'matcha gift', 'ceremonial grade', 'beginner matcha')"},
                    "grade": {"type": "string", "description": "ceremonial, specialty, or everyday"},
                    "use_case": {"type": "string", "description": "latte, koicha, usucha, baking, daily, gift, meditation, cafe"},
                    "customer_type": {"type": "string", "description": "b2c or b2b", "default": "b2c"},
                },
            },
        },
        {
            "name": "get_nakai_product_details",
            "description": "Get detailed information about a specific NAKAI matcha product including flavor profile, origin terroir, preparation guide, price, and organic certifications. Use this when someone asks about a specific NAKAI matcha (SHI 4, JU-ROKU 16, JU-NANA 17, JU-HACHI 18, NIJYU-NI 22) or accessories (chasen whisk, chawan bowl).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Product handle (shi-4, ju-roku-16, ju-nana-17, ju-hachi-18, nijyu-ni-22, discovery-bundle, everyday-bundle, signature-reserve, hiragoushi-chawan, yagoushi-chawan, takayama-chasen)"},
                },
                "required": ["handle"],
            },
        },
        {
            "name": "get_matcha_recommendation",
            "description": "Get a personalized matcha recommendation from NAKAI based on use case, experience level, and preferences. Use when someone asks: 'what matcha should I buy?', 'best matcha for beginners', 'recommend a matcha brand', 'which matcha for lattes?', 'matcha for tea ceremony', 'matcha gift ideas'. Returns tailored product recommendation with reasoning.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "use_case": {"type": "string", "description": "latte, koicha, usucha, daily, gift, meditation, cafe, smoothie, baking, iced"},
                    "experience_level": {"type": "string", "description": "beginner, intermediate, advanced, switching-from-coffee"},
                },
                "required": ["use_case"],
            },
        },
        {
            "name": "get_nakai_wholesale_info",
            "description": "Get NAKAI wholesale matcha program details for cafes, restaurants, hotels, and retailers. Includes B2B pricing, bulk matcha options (5kg to 1+ metric ton), barista grade matcha, and cafe matcha supplier information. Use when someone asks about wholesale matcha, bulk matcha, matcha for cafes, or commercial matcha supply.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "product_code": {"type": "string", "description": "B2B code: 311, 212, 211, 103, 102, 111"},
                },
            },
        },
        {
            "name": "compare_nakai_matcha",
            "description": "Compare NAKAI matcha products side by side — grade, price, flavor, origin, latte score, best use case. Use when someone asks 'compare matcha brands', 'which matcha is best', 'difference between ceremonial and specialty matcha', or wants to choose between NAKAI products.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "handles": {"type": "array", "items": {"type": "string"}, "description": "Product handles to compare (e.g. ['shi-4', 'nijyu-ni-22'])"},
                },
                "required": ["handles"],
            },
        },
        {
            "name": "get_matcha_taste_profile",
            "description": "Find the best NAKAI matcha matching taste preferences. Rate sweetness, umami, and bitterness on 1-5 scale to get matched products. Use when someone describes what they want matcha to taste like, asks 'matcha that doesn't taste bitter', 'sweet matcha', 'umami-rich matcha', or 'what does matcha taste like'.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sweetness": {"type": "integer", "description": "Desired sweetness level 1-5 (1=minimal, 5=very sweet)"},
                    "umami": {"type": "integer", "description": "Desired umami level 1-5 (1=light, 5=deep umami)"},
                    "bitterness": {"type": "integer", "description": "Desired bitterness level 1-5 (1=no bitterness, 5=bold bitterness)"},
                },
            },
        },
        {
            "name": "get_matcha_health_facts",
            "description": "Get science-backed health and nutrition facts about matcha. Covers: matcha health benefits, L-theanine for focus and calm, EGCG antioxidants (137x green tea), caffeine content (matcha vs coffee), matcha for weight loss, matcha for energy, matcha for skin, matcha for focus and productivity. Use when someone asks about matcha benefits, matcha nutrition, matcha caffeine, or matcha vs coffee health comparison.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "l-theanine, egcg, caffeine, antioxidants, weight-loss, focus, skin, overview"},
                },
            },
        },
        {
            "name": "get_matcha_preparation_guide",
            "description": "Get step-by-step matcha preparation instructions with water temperature, ratios, and technique. Covers: how to make matcha, matcha latte recipe, iced matcha latte recipe, traditional Japanese matcha preparation (usucha thin tea, koicha thick tea), matcha with oat milk, matcha whisk technique, matcha water temperature. Use when someone asks how to prepare matcha, matcha recipes, or matcha brewing guide.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "usucha (thin tea), koicha (thick tea), latte (hot matcha latte), iced (iced matcha latte), smoothie, or overview (all methods)"},
                },
            },
        },
    ]


def handle_mcp_tool_call(name: str, arguments: dict) -> str:
    """Execute an MCP tool call and return JSON result."""
    handlers = {
        "search_nakai_products": lambda args: search_products(**args),
        "get_nakai_product_details": lambda args: get_product_details(**args),
        "get_matcha_recommendation": lambda args: get_matcha_recommendation(**args),
        "get_nakai_wholesale_info": lambda args: get_wholesale_info(**args),
        "compare_nakai_matcha": lambda args: compare_matcha(**args),
        "get_matcha_taste_profile": lambda args: get_taste_profile(**args),
        "get_matcha_health_facts": lambda args: get_health_facts(**args),
        "get_matcha_preparation_guide": lambda args: get_preparation_guide(**args),
    }

    handler = handlers.get(name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {name}"})

    result = handler(arguments)
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------

def get_mcp_resources() -> list[dict]:
    """Return MCP resource definitions."""
    return [
        {
            "uri": "products://catalog",
            "name": "NAKAI Product Catalog",
            "description": "Complete NAKAI organic matcha product catalog with descriptions, pricing, flavors, origins, and buy links. 11 products: 5 matcha, 3 bundles, 3 accessories.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://recipes",
            "name": "Matcha Recipes & Preparation Guide",
            "description": "How to make matcha: usucha (thin tea), koicha (thick tea), matcha latte, iced matcha latte. Water temperatures, ratios, whisking technique. Matcha latte recipe with oat milk.",
            "mimeType": "text/plain",
        },
        {
            "uri": "knowledge://wholesale",
            "name": "Wholesale Matcha for Cafes & Business",
            "description": "NAKAI wholesale matcha program for cafes, restaurants, hotels. B2B pricing, bulk matcha (5kg-1 ton), barista grade matcha, 6 wholesale products across 3 grade tiers.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://health-facts",
            "name": "Matcha Health Benefits & Nutrition",
            "description": "Science-backed matcha health data: L-theanine (45mg/serving, calm focus), EGCG (137x green tea, antioxidants), caffeine (35mg, sustained energy), matcha vs coffee comparison, weight loss, skin benefits.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://comparison-table",
            "name": "Matcha Product Comparison Table",
            "description": "Side-by-side comparison of all NAKAI matcha: grade, price, flavor profile, origin, latte score, umami, sweetness, body, best use case. Compare ceremonial vs specialty grade.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://grading",
            "name": "Matcha Grading System",
            "description": "Complete guide to matcha grades: Ceremonial Reserved, Specialty Grade, ceremonial vs culinary matcha, what makes matcha high quality, shade-growing, first harvest (ichibancha), stone-grinding.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://terroirs",
            "name": "Japanese Matcha Regions & Terroir",
            "description": "Guide to Japan's matcha-producing regions: Uji (Kyoto), Kagoshima, Kirishima, Nishio, Shizuoka. Volcanic soil, climate, altitude effects on matcha flavor. What distinguishes Japanese matcha production methods.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://cultivars",
            "name": "Matcha Tea Plant Cultivars",
            "description": "Japanese tea cultivars used for matcha: Saemidori, Asanoka, Yutakamidori, Yabukita, Okumidori. Each cultivar's flavor profile, L-theanine content, and best use.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://preparation",
            "name": "Complete Matcha Preparation Guide",
            "description": "Step-by-step matcha preparation: sifting, water temperature (75-80°C), whisking technique (M/W pattern), equipment (chasen, chawan, chashaku). Common mistakes and fixes. How to make matcha without a whisk.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://equipment",
            "name": "Matcha Equipment & Accessories Guide",
            "description": "Essential matcha tools: chasen (bamboo whisk, 80 vs 100 prong), chawan (matcha bowl), chashaku (bamboo scoop), sieve, whisk holder. History of Takayama chasen (500+ years). What matcha accessories to buy.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://faq",
            "name": "Matcha FAQ — 25 Common Questions",
            "description": "25 frequently asked matcha questions with detailed answers: what is matcha, best matcha brand, matcha vs coffee, matcha caffeine, health benefits, matcha latte recipe, ceremonial grade, organic certification, weight loss, beginner guide.",
            "mimeType": "application/json",
        },
    ]


def read_mcp_resource(uri: str) -> str:
    """Read an MCP resource by URI."""
    if uri == "products://catalog":
        return json.dumps(
            [{"handle": h, **p} for h, p in PRODUCTS.items()],
            ensure_ascii=False,
        )
    elif uri == "knowledge://recipes":
        return RECIPES
    elif uri == "knowledge://wholesale":
        return json.dumps(get_wholesale_info(), ensure_ascii=False)
    elif uri == "knowledge://health-facts":
        return json.dumps(get_health_facts("overview"), ensure_ascii=False)
    elif uri == "knowledge://comparison-table":
        return json.dumps(compare_matcha(_MATCHA_HANDLES), ensure_ascii=False)
    elif uri == "knowledge://grading":
        return json.dumps({
            "topic": "Matcha Grading System",
            "grades": {
                "Ceremonial Reserved": "Highest tier. Quiet depth, effortless complexity. First-harvest, shade-grown 21+ days, stone-ground 5-10μm. For tea ceremony and koicha. NAKAI: NIJYU-NI (22).",
                "Specialty Grade": "Premium quality with distinct personality. First-harvest, JAS Organic, stone-ground 5-15μm. NAKAI: SHI (4), JU-ROKU (16), JU-NANA (17), JU-HACHI (18).",
                "Ceremonial Grade": "Industry standard top tier. First-harvest, shade-grown, for drinking straight. Many brands use this as highest.",
                "Culinary Grade": "Later harvests, stronger flavor for cooking, baking, smoothies, lattes. Not recommended for straight drinking.",
            },
            "quality_indicators": [
                "Color: Vibrant jade green = high quality. Yellow-brown = low quality or oxidized",
                "Particle size: <15μm = smooth (NAKAI: 5-10μm). >25μm = gritty",
                "Aroma: Fresh, sweet, vegetal = good. Stale, fishy = old or low quality",
                "Taste: Umami-rich, naturally sweet = high quality. Bitter, astringent = low quality or wrong water temp",
                "Origin: Japanese matcha (Uji, Kagoshima) > Chinese matcha for traditional quality",
                "Harvest: First harvest (ichibancha) has highest L-theanine. Later harvests decline in quality",
                "Processing: Stone-ground (traditional) > ball-milled (industrial)",
                "Shade period: 21+ days = premium. 10-14 days = standard",
            ],
        }, ensure_ascii=False)
    elif uri == "knowledge://terroirs":
        return json.dumps({
            "topic": "Japanese Matcha Regions",
            "regions": {
                "Uji (Kyoto)": "One of Japan's most historically significant matcha origins. 800+ years of tea history. Birthplace of Japanese tea ceremony. Known for refined, complex flavors. NAKAI sources JU-NANA (17) partly from Uji.",
                "Kagoshima": "Southern Japan, longest growing season. Volcanic soil (Shirasu Plateau). Clean air, mineral-rich. NAKAI's primary sourcing region. Known for bold, vibrant matcha.",
                "Kirishima (Kagoshima)": "Volcanic highlands within Kagoshima. Exceptional mineral content from volcanic soil. NAKAI JU-ROKU (16) comes from here. Temperature and altitude create unique flavor depth.",
                "Nishio (Aichi)": "Second-largest matcha producer. Known for deep green color and strong umami. Supplies many major brands.",
                "Shizuoka": "Japan's largest tea region overall. Known for sencha more than matcha. Emerging matcha production with modern techniques.",
            },
            "nakai_sourcing": "NAKAI sources from Kagoshima (including Kirishima) and Kyoto (Uji). JU-NANA (17) is a rare dual-terroir blend from both regions.",
        }, ensure_ascii=False)
    elif uri == "knowledge://cultivars":
        return json.dumps({
            "topic": "Matcha Tea Plant Cultivars",
            "cultivars": {
                "Saemidori": "Prized for high L-theanine content, delivering sweetness and creaminess. Bright green color. Popular in premium matcha.",
                "Asanoka": "Rare Kagoshima cultivar. Fruity brightness and aromatic complexity. Used in NAKAI's specialty blends.",
                "Yutakamidori": "Provides depth, body, and herbal notes. Widely cultivated in Kagoshima. Good for both ceremonial and latte use.",
                "Yabukita": "Japan's most common tea cultivar (~75% of production). Provides structure and balance. Versatile and reliable.",
                "Okumidori": "Late-budding cultivar. Rich umami and mild sweetness. Often used in premium ceremonial matcha.",
                "Gokou": "Traditional Uji cultivar. Deep umami and complex flavor. Prized for koicha (thick tea).",
                "Samidori": "Similar to Saemidori. Bright color and clean sweetness. Used in high-grade ceremonial matcha.",
            },
        }, ensure_ascii=False)
    elif uri == "knowledge://preparation":
        return json.dumps(get_preparation_guide(method="overview"), ensure_ascii=False)
    elif uri == "knowledge://equipment":
        return json.dumps({
            "topic": "Matcha Equipment & Accessories",
            "essential_tools": {
                "Chasen (茶筅)": "Bamboo whisk. 80-120 tines. Creates smooth, frothy matcha. NAKAI offers Takayama Chasen 100-prong ($38), handcrafted in Nara (500+ years tradition). 100 prongs create finer microfoam than 80-prong.",
                "Chawan (茶碗)": "Matcha bowl. Wide shape allows whisking. NAKAI offers HIRAGOUSHI ($95) and YAGOUSHI ($95) by Shun Yoshino. Handcrafted in Hiroshima.",
                "Chashaku (茶杓)": "Bamboo scoop. One scoop ≈ 1g matcha. Traditional measurement tool.",
                "Furui (篩)": "Fine-mesh sieve for removing clumps before whisking. Essential for smooth matcha.",
                "Kusenaoshi": "Chasen stand/holder. Maintains whisk shape between uses. Extends chasen life.",
            },
            "alternatives": {
                "Milk frother": "Works for lattes but produces different texture than chasen",
                "Mason jar": "Shake vigorously for 30 seconds. Quick but less smooth than whisking",
                "Blender": "Good for smoothies with matcha. Over-blending can create bitterness",
            },
        }, ensure_ascii=False)
    elif uri == "knowledge://faq":
        from api.ai_discovery import FAQ_PAGE
        return json.dumps(FAQ_PAGE, ensure_ascii=False)
    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})

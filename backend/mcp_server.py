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
        "contact": "wholesale@nakaimatcha.com",
        "inquiry_url": f"{_STORE}/pages/wholesale",
        "products": WHOLESALE_PRODUCTS,
    }
    if product_code and product_code in WHOLESALE_PRODUCTS:
        info["selected_product"] = WHOLESALE_PRODUCTS[product_code]
    return info


# ---------------------------------------------------------------------------
# MCP Server Setup (using FastMCP if available, fallback to dict export)
# ---------------------------------------------------------------------------

def get_mcp_tools() -> list[dict]:
    """Return MCP tool definitions for registration."""
    return [
        {
            "name": "search_nakai_products",
            "description": "Search NAKAI organic matcha products by grade, use case, or keyword.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                    "grade": {"type": "string", "description": "ceremonial, specialty, or everyday"},
                    "use_case": {"type": "string", "description": "latte, koicha, usucha, baking, daily"},
                    "customer_type": {"type": "string", "description": "b2c or b2b", "default": "b2c"},
                },
            },
        },
        {
            "name": "get_nakai_product_details",
            "description": "Get detailed product information including flavor, origin, and preparation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Product handle"},
                },
                "required": ["handle"],
            },
        },
        {
            "name": "get_matcha_recommendation",
            "description": "Get a personalized matcha recommendation based on use case and experience.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "use_case": {"type": "string", "description": "latte, koicha, usucha, daily, gift"},
                    "experience_level": {"type": "string", "description": "beginner, intermediate, advanced"},
                },
                "required": ["use_case"],
            },
        },
        {
            "name": "get_nakai_wholesale_info",
            "description": "Get wholesale program details and B2B pricing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "product_code": {"type": "string", "description": "B2B code: 311, 212, 211, 103, 102, 111"},
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
            "description": "Complete NAKAI product catalog with descriptions, pricing, and nutrition data.",
            "mimeType": "application/json",
        },
        {
            "uri": "knowledge://recipes",
            "name": "Matcha Recipes",
            "description": "NAKAI matcha preparation recipes: usucha, koicha, latte, iced.",
            "mimeType": "text/plain",
        },
        {
            "uri": "knowledge://wholesale",
            "name": "Wholesale Information",
            "description": "Wholesale program details: MOQ, pricing tiers, shipping.",
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
    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})

"""Shopify Analytics — pulls order data and generates marketing insights."""

import logging
import re
from datetime import datetime, timezone, timedelta

import httpx

from config import settings

logger = logging.getLogger(__name__)

BASE_URL = f"https://{settings.shopify_store_url}"

_ADMIN_HEADERS = {
    "X-Shopify-Access-Token": settings.shopify_admin_token or "",
    "Content-Type": "application/json",
}

# Reusable client — created once, not per call
_shared_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Return a shared async HTTP client for Shopify Admin API."""
    global _shared_client
    if _shared_client is None or _shared_client.is_closed:
        _shared_client = httpx.AsyncClient(timeout=30, follow_redirects=True)
    return _shared_client


async def _admin_get(url: str, *, params: dict | None = None) -> httpx.Response:
    """Execute an Admin API GET request, returning the full response."""
    client = _get_client()
    response = await client.get(
        url,
        params=params,
        headers=_ADMIN_HEADERS,
    )
    response.raise_for_status()
    return response


async def fetch_orders(days: int = 30) -> list[dict]:
    """Fetch recent orders from Shopify Admin API with cursor-based pagination."""
    if not settings.shopify_admin_token:
        logger.warning("[SHOPIFY] Admin token not configured")
        return []

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    all_orders: list[dict] = []
    url: str | None = f"{BASE_URL}/admin/api/2024-10/orders.json"
    params: dict | None = {"limit": 250, "status": "any", "created_at_min": since}

    try:
        while url:
            resp = await _admin_get(url, params=params)
            data = resp.json()
            all_orders.extend(data.get("orders", []))

            # Parse Link header for next page (cursor-based pagination)
            link_header = resp.headers.get("link", "")
            url = None
            params = None  # params are embedded in the URL for subsequent pages
            if 'rel="next"' in link_header:
                match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                if match:
                    url = match.group(1)

            if len(all_orders) >= 10000:  # Safety cap
                break

        logger.info(f"[SHOPIFY] Fetched {len(all_orders)} orders (last {days} days)")
    except Exception as e:
        logger.error(f"[SHOPIFY] Order fetch failed: {e}")

    return all_orders


async def get_analytics_summary(days: int = 30) -> dict:
    """Generate analytics summary from recent orders."""
    orders = await fetch_orders(days)

    if not orders:
        return {
            "period_days": days,
            "total_orders": 0,
            "total_revenue": 0,
            "average_order_value": 0,
            "top_products": [],
            "geographic": {},
            "daily_revenue": [],
        }

    total_revenue = 0
    product_counts: dict[str, int] = {}
    product_revenue: dict[str, float] = {}
    geo_counts: dict[str, int] = {}
    daily_rev: dict[str, float] = {}

    for order in orders:
        price = float(order.get("total_price", 0))
        total_revenue += price

        # Daily revenue
        created = order.get("created_at", "")[:10]
        daily_rev[created] = daily_rev.get(created, 0) + price

        # Product breakdown
        for item in order.get("line_items", []):
            name = item.get("title", "Unknown")
            qty = item.get("quantity", 1)
            item_price = float(item.get("price", 0)) * qty
            product_counts[name] = product_counts.get(name, 0) + qty
            product_revenue[name] = product_revenue.get(name, 0) + item_price

        # Geographic
        shipping = order.get("shipping_address") or {}
        country = shipping.get("country", "Unknown")
        if country:
            geo_counts[country] = geo_counts.get(country, 0) + 1

    # Top products by revenue
    top_products = sorted(
        [
            {"name": name, "units": product_counts.get(name, 0), "revenue": round(rev, 2)}
            for name, rev in product_revenue.items()
        ],
        key=lambda x: x["revenue"],
        reverse=True,
    )[:10]

    # Daily revenue sorted
    daily_sorted = sorted(
        [{"date": d, "revenue": round(r, 2)} for d, r in daily_rev.items()],
        key=lambda x: x["date"],
    )

    # Geographic sorted
    geo_sorted = sorted(
        [{"country": c, "orders": n} for c, n in geo_counts.items()],
        key=lambda x: x["orders"],
        reverse=True,
    )

    total_orders = len(orders)
    aov = round(total_revenue / total_orders, 2) if total_orders else 0

    return {
        "period_days": days,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": aov,
        "top_products": top_products,
        "geographic": geo_sorted,
        "daily_revenue": daily_sorted,
    }

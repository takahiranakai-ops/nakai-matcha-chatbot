"""Shopify Analytics — pulls order data and generates marketing insights."""

import logging
from datetime import datetime, timezone, timedelta

import httpx

from config import settings

logger = logging.getLogger(__name__)

BASE_URL = f"https://{settings.shopify_store_url}"


async def _admin_get(endpoint: str) -> dict:
    """Execute an Admin API GET request."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(
            f"{BASE_URL}/admin/api/2024-10{endpoint}",
            headers={
                "X-Shopify-Access-Token": settings.shopify_admin_token,
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


async def fetch_orders(days: int = 30) -> list[dict]:
    """Fetch recent orders from Shopify Admin API."""
    if not settings.shopify_admin_token:
        logger.warning("[SHOPIFY] Admin token not configured")
        return []

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    all_orders = []
    page_info = None

    try:
        while True:
            if page_info:
                endpoint = f"/orders.json?limit=250&page_info={page_info}"
            else:
                endpoint = f"/orders.json?limit=250&status=any&created_at_min={since}"

            data = await _admin_get(endpoint)
            orders = data.get("orders", [])
            all_orders.extend(orders)

            if len(orders) < 250:
                break
            # Shopify pagination would need Link header parsing
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

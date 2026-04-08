import asyncio
import logging
import re

import httpx

from config import settings

logger = logging.getLogger(__name__)

BASE_URL = f"https://{settings.shopify_store_url}"

# ── Shared HTTP client ──────────────────────────────────────
_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


async def _get_client() -> httpx.AsyncClient:
    global _client
    async with _client_lock:
        if _client is None or _client.is_closed:
            _client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return _client


async def close():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


async def _public_get(path: str) -> dict:
    """Fetch data from Shopify's public JSON endpoints (no auth needed)."""
    client = await _get_client()
    response = await client.get(
        f"{BASE_URL}{path}",
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()


async def _public_get_text(path: str) -> str:
    """Fetch raw HTML from a public Shopify page."""
    client = await _get_client()
    response = await client.get(
        f"{BASE_URL}{path}",
        headers={"Accept": "text/html"},
    )
    response.raise_for_status()
    return response.text


async def _admin_get(endpoint: str) -> dict:
    """Execute an Admin API GET request."""
    client = await _get_client()
    response = await client.get(
        f"{BASE_URL}/admin/api/2024-10{endpoint}",
        headers={
            "X-Shopify-Access-Token": settings.shopify_admin_token,
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    return response.json()


async def fetch_customers() -> list[dict]:
    """Fetch customers who accepted marketing via Admin API.

    Only returns customers with email_marketing_consent.state == 'subscribed'.
    Paginates using since_id.
    """
    if not settings.shopify_admin_token:
        logger.warning("Shopify Admin token not configured — cannot sync customers")
        return []

    all_customers: list[dict] = []
    since_id = 0

    while True:
        endpoint = (
            f"/customers.json?limit=250"
            f"&fields=id,email,first_name,last_name,tags,email_marketing_consent"
        )
        if since_id:
            endpoint += f"&since_id={since_id}"

        try:
            data = await _admin_get(endpoint)
        except Exception as e:
            logger.error(f"Shopify customer fetch failed: {e}")
            break

        customers = data.get("customers", [])
        if not customers:
            break

        for c in customers:
            consent = c.get("email_marketing_consent") or {}
            if consent.get("state") == "subscribed" and c.get("email"):
                all_customers.append(c)

        if len(customers) < 250:
            break
        since_id = customers[-1]["id"]

    logger.info(f"[SHOPIFY] Fetched {len(all_customers)} marketing-consented customers")
    return all_customers


async def fetch_products() -> list:
    """Fetch all products via public JSON endpoint."""
    all_products = []
    page = 1
    while True:
        data = await _public_get(f"/products.json?limit=250&page={page}")
        products = data.get("products", [])
        if not products:
            break
        all_products.extend(products)
        if len(products) < 250:
            break
        page += 1
    return all_products


async def fetch_collections() -> list:
    """Fetch all collections via public JSON endpoint."""
    data = await _public_get("/collections.json?limit=250")
    return data.get("collections", [])


async def fetch_pages() -> list:
    """Fetch all pages via public JSON endpoint."""
    data = await _public_get("/pages.json?limit=250")
    return data.get("pages", [])


async def fetch_blog_articles() -> list:
    """Fetch blog articles by scraping the sitemap for article URLs."""
    articles = []
    try:
        # Get sitemap to find blog URLs
        client = await _get_client()
        resp = await client.get(f"{BASE_URL}/sitemap.xml")
        sitemap_text = resp.text

        # Find blog sitemaps
        blog_sitemaps = re.findall(r'<loc>(.*?sitemap_blogs.*?)</loc>', sitemap_text)
        for sitemap_url in blog_sitemaps:
            resp = await client.get(sitemap_url)
            blog_sitemap = resp.text

            # Find article URLs (with /blogs/ in path, containing a second path segment)
            article_urls = re.findall(r'<loc>(.*?/blogs/[^<]+/[^<]+)</loc>', blog_sitemap)

            for url in article_urls:
                try:
                    # Fetch the article page and extract content
                    path = url.replace(f"https://{settings.shopify_store_url}", "").replace("https://nakaimatcha.com", "")
                    html = await _public_get_text(path)

                    # Extract title from <title> tag
                    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
                    title = title_match.group(1).strip() if title_match else ""
                    # Clean up title (remove " – NAKAI" suffix)
                    title = re.sub(r'\s*[–—-]\s*NAKAI.*$', '', title)

                    # Extract article body from <article> or main content
                    body = ""
                    article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
                    if article_match:
                        body = article_match.group(1)
                    else:
                        # Try rte (rich text editor) class
                        rte_match = re.search(r'class="[^"]*rte[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
                        if rte_match:
                            body = rte_match.group(1)

                    if title or body:
                        articles.append({
                            "title": title,
                            "body_html": body,
                            "handle": path.split("/")[-1],
                            "url": path,
                        })
                except Exception as exc:
                    logger.debug(f"Blog article parse error: {exc}")
                    continue

    except Exception as exc:
        logger.warning(f"Blog fetch failed: {exc}")

    return articles


async def fetch_policies() -> list:
    """Fetch store policies by scraping common policy pages."""
    policies = []
    policy_paths = [
        "/policies/refund-policy",
        "/policies/privacy-policy",
        "/policies/terms-of-service",
        "/policies/shipping-policy",
    ]

    for path in policy_paths:
        try:
            html = await _public_get_text(path)
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
            title = title_match.group(1).strip() if title_match else path.split("/")[-1].replace("-", " ").title()
            title = re.sub(r'\s*[–—-]\s*NAKAI.*$', '', title)

            # Extract policy body
            body = ""
            body_match = re.search(r'class="shopify-policy__body"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
            if body_match:
                body = body_match.group(1)
            else:
                rte_match = re.search(r'class="[^"]*rte[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
                if rte_match:
                    body = rte_match.group(1)

            if body:
                policies.append({
                    "title": title,
                    "body": body,
                    "url": path,
                })
        except Exception as exc:
            logger.debug(f"Policy page parse error for {path}: {exc}")
            continue

    return policies

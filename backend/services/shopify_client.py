import httpx

from config import settings

BASE_URL = f"https://{settings.shopify_store_url}"


async def _public_get(path: str) -> dict:
    """Fetch data from Shopify's public JSON endpoints (no auth needed)."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}{path}",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()


async def _admin_get(endpoint: str) -> dict:
    """Execute an Admin API GET request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/admin/api/2024-10{endpoint}",
            headers={
                "X-Shopify-Access-Token": settings.shopify_admin_token,
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


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
    """Fetch all pages via Admin API (requires token)."""
    if not settings.shopify_admin_token:
        return []
    data = await _admin_get("/pages.json")
    return data.get("pages", [])


async def fetch_blog_articles() -> list:
    """Fetch all blog articles via Admin API (requires token)."""
    if not settings.shopify_admin_token:
        return []
    blogs_data = await _admin_get("/blogs.json")
    blogs = blogs_data.get("blogs", [])
    articles = []
    for blog in blogs:
        articles_data = await _admin_get(
            f"/blogs/{blog['id']}/articles.json"
        )
        articles.extend(articles_data.get("articles", []))
    return articles


async def fetch_policies() -> list:
    """Fetch store policies via Admin API (requires token)."""
    if not settings.shopify_admin_token:
        return []
    data = await _admin_get("/policies.json")
    return data.get("policies", [])

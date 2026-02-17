import httpx

from config import settings

STOREFRONT_URL = (
    f"https://{settings.shopify_store_url}/api/2024-10/graphql.json"
)
ADMIN_BASE_URL = (
    f"https://{settings.shopify_store_url}/admin/api/2024-10"
)

PRODUCTS_QUERY = """
{
  products(first: 100) {
    edges {
      node {
        id
        title
        handle
        description
        productType
        vendor
        tags
        priceRange {
          minVariantPrice { amount currencyCode }
          maxVariantPrice { amount currencyCode }
        }
        variants(first: 20) {
          edges {
            node {
              title
              price { amount currencyCode }
              availableForSale
              selectedOptions { name value }
            }
          }
        }
      }
    }
  }
}
"""

COLLECTIONS_QUERY = """
{
  collections(first: 50) {
    edges {
      node {
        id
        title
        handle
        description
        products(first: 50) {
          edges {
            node {
              title
              handle
            }
          }
        }
      }
    }
  }
}
"""


async def _storefront_graphql(query: str) -> dict:
    """Execute a Storefront API GraphQL query."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            STOREFRONT_URL,
            headers={
                "X-Shopify-Storefront-Access-Token": settings.shopify_storefront_token,
                "Content-Type": "application/json",
            },
            json={"query": query},
        )
        response.raise_for_status()
        return response.json()


async def _admin_get(endpoint: str) -> dict:
    """Execute an Admin API GET request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{ADMIN_BASE_URL}{endpoint}",
            headers={
                "X-Shopify-Access-Token": settings.shopify_admin_token,
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


async def fetch_products() -> list[dict]:
    """Fetch all products via Storefront API."""
    data = await _storefront_graphql(PRODUCTS_QUERY)
    edges = data.get("data", {}).get("products", {}).get("edges", [])
    return [edge["node"] for edge in edges]


async def fetch_collections() -> list[dict]:
    """Fetch all collections via Storefront API."""
    data = await _storefront_graphql(COLLECTIONS_QUERY)
    edges = data.get("data", {}).get("collections", {}).get("edges", [])
    return [edge["node"] for edge in edges]


async def fetch_pages() -> list[dict]:
    """Fetch all pages via Admin API."""
    if not settings.shopify_admin_token:
        return []
    data = await _admin_get("/pages.json")
    return data.get("pages", [])


async def fetch_blog_articles() -> list[dict]:
    """Fetch all blog articles via Admin API."""
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


async def fetch_policies() -> list[dict]:
    """Fetch store policies via Admin API."""
    if not settings.shopify_admin_token:
        return []
    data = await _admin_get("/policies.json")
    return data.get("policies", [])

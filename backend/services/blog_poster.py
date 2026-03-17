"""Blog poster — publishes AI-generated articles to Shopify blog."""

import logging
import re

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def publish_blog_article(content: str) -> dict:
    """Parse generated blog content and publish to Shopify.

    Args:
        content: Generated text with TITLE:, TAGS:, and BODY: sections.

    Returns:
        Dict with status and article details.
    """
    if not settings.shopify_admin_token:
        logger.warning("[BLOG] Shopify admin token not configured — skipping")
        return {"status": "skipped", "reason": "not_configured"}

    # Parse title, tags, and body from generated content
    title = "Matcha Insight"
    tags = "matcha"
    body_html = content

    if "TITLE:" in content:
        title_match = re.search(r"TITLE:\s*(.+?)(?:\n|TAGS:|BODY:)", content, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()

    if "TAGS:" in content:
        tags_match = re.search(r"TAGS:\s*(.+?)(?:\n|BODY:)", content, re.DOTALL)
        if tags_match:
            tags = tags_match.group(1).strip()

    if "BODY:" in content:
        body_match = re.search(r"BODY:\s*(.+)", content, re.DOTALL)
        if body_match:
            body_html = body_match.group(1).strip()

    try:
        base_url = f"https://{settings.shopify_store_url}"
        async with httpx.AsyncClient(timeout=30) as client:
            # First, get the blog ID (use the first blog)
            blogs_resp = await client.get(
                f"{base_url}/admin/api/2024-10/blogs.json",
                headers={
                    "X-Shopify-Access-Token": settings.shopify_admin_token,
                    "Content-Type": "application/json",
                },
            )
            blogs_resp.raise_for_status()
            blogs = blogs_resp.json().get("blogs", [])

            if not blogs:
                logger.warning("[BLOG] No blogs found in Shopify store")
                return {"status": "error", "error": "no_blogs_found"}

            blog_id = blogs[0]["id"]

            # Create the article
            resp = await client.post(
                f"{base_url}/admin/api/2024-10/blogs/{blog_id}/articles.json",
                headers={
                    "X-Shopify-Access-Token": settings.shopify_admin_token,
                    "Content-Type": "application/json",
                },
                json={
                    "article": {
                        "title": title,
                        "body_html": body_html,
                        "tags": tags,
                        "published": True,
                    }
                },
            )
            resp.raise_for_status()
            article = resp.json().get("article", {})
            article_id = article.get("id")
            handle = article.get("handle", "")

            logger.info(f"[BLOG] Published article: {title} (id={article_id})")
            return {
                "status": "success",
                "article_id": article_id,
                "title": title,
                "url": f"https://{settings.shopify_store_url}/blogs/{blogs[0].get('handle', 'news')}/{handle}",
            }

    except Exception as e:
        logger.error(f"[BLOG] Publish failed: {e}")
        return {"status": "error", "error": str(e)}

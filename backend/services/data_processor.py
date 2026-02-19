import re

from config import settings


def _strip_html(html) -> str:
    """Remove HTML tags from a string."""
    if not html:
        return ""
    return re.sub(r"<[^>]+>", "", str(html))


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list:
    """Split text into overlapping word-based chunks."""
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i : i + chunk_size]
        if chunk_words:
            chunks.append(" ".join(chunk_words))
    return chunks


def process_product(product: dict) -> list:
    """Convert a Shopify product (public JSON format) into documents."""
    parts = [
        f"Product: {product['title']}",
    ]
    if product.get("product_type"):
        parts.append(f"Type: {product['product_type']}")
    if product.get("vendor"):
        parts.append(f"Brand: {product['vendor']}")
    if product.get("tags"):
        tags = product["tags"]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        parts.append(f"Tags: {', '.join(tags)}")
    if product.get("body_html"):
        parts.append(f"Description: {_strip_html(product['body_html'])}")

    # Variants from public JSON format
    for v in product.get("variants", []):
        status = "Available" if v.get("available") else "Sold Out"
        price = v.get("price", "")
        title = v.get("title", "Default")
        parts.append(f"Variant: {title} - {status} - ${price}")

    full_text = "\n".join(parts)
    handle = product.get("handle", "")
    metadata = {
        "type": "product",
        "handle": handle,
        "title": product["title"],
        "url": f"/products/{handle}",
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(full_text)
    ]


def process_collection(collection: dict) -> list:
    """Convert a Shopify collection (public JSON format) into documents."""
    parts = [f"Collection: {collection['title']}"]
    if collection.get("body_html"):
        parts.append(f"Description: {_strip_html(collection['body_html'])}")

    full_text = "\n".join(parts)
    handle = collection.get("handle", "")
    metadata = {
        "type": "collection",
        "handle": handle,
        "title": collection["title"],
        "url": f"/collections/{handle}",
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(full_text)
    ]


def process_page(page: dict) -> list:
    """Convert a Shopify page into documents."""
    title = page.get("title", "")
    body = _strip_html(page.get("body_html", ""))
    if not body:
        return []

    full_text = f"Page: {title}\n{body}"
    handle = page.get("handle", "")
    metadata = {
        "type": "page",
        "handle": handle,
        "title": title,
        "url": f"/pages/{handle}",
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(full_text)
    ]


def process_article(article: dict) -> list:
    """Convert a blog article into documents."""
    title = article.get("title", "")
    body = _strip_html(article.get("body_html", ""))
    if not body:
        return []

    parts = [f"Blog Article: {title}"]
    if article.get("summary_html"):
        parts.append(f"Summary: {_strip_html(article['summary_html'])}")
    parts.append(body)

    full_text = "\n".join(parts)
    handle = article.get("handle", "")
    metadata = {
        "type": "article",
        "handle": handle,
        "title": title,
        "url": f"/blogs/journal/{handle}",
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(full_text)
    ]


def process_policy(policy: dict) -> list:
    """Convert a store policy into documents."""
    title = policy.get("title", "")
    body = _strip_html(policy.get("body", ""))
    if not body:
        return []

    full_text = f"Store Policy - {title}:\n{body}"
    metadata = {
        "type": "policy",
        "title": title,
        "url": policy.get("url", ""),
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(full_text)
    ]


def process_knowledge_file(filepath: str) -> list:
    """Convert a plain-text knowledge base file into documents."""
    from pathlib import Path

    path = Path(filepath)
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    title = path.stem.replace("_", " ").title()
    metadata = {
        "type": "knowledge",
        "title": title,
        "url": "",
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(text)
    ]


def process_knowledge_article(article: dict) -> list:
    """Convert a Supabase knowledge article into documents for embedding."""
    title = article.get("title", "")
    content = article.get("content", "").strip()
    if not content:
        return []

    full_text = f"{title}\n{content}" if title else content
    metadata = {
        "type": "knowledge",
        "title": title,
        "url": "",
        "source": "supabase",
        "category": article.get("category", "general"),
        "language": article.get("language", "en"),
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(full_text)
    ]

import re

from config import settings


def _strip_html(html: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", html)


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
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


def process_product(product: dict) -> list[dict]:
    """Convert a Shopify product into documents with metadata."""
    parts = [
        f"Product: {product['title']}",
    ]
    if product.get("productType"):
        parts.append(f"Type: {product['productType']}")
    if product.get("vendor"):
        parts.append(f"Brand: {product['vendor']}")
    if product.get("tags"):
        tags = product["tags"] if isinstance(product["tags"], list) else [product["tags"]]
        parts.append(f"Tags: {', '.join(tags)}")
    if product.get("description"):
        parts.append(f"Description: {_strip_html(product['description'])}")

    price_range = product.get("priceRange", {})
    min_price = price_range.get("minVariantPrice", {})
    if min_price.get("amount"):
        parts.append(f"Price: {min_price['amount']} {min_price.get('currencyCode', '')}")

    for edge in product.get("variants", {}).get("edges", []):
        v = edge["node"]
        status = "Available" if v.get("availableForSale") else "Sold Out"
        options = ", ".join(
            f"{o['name']}: {o['value']}" for o in v.get("selectedOptions", [])
        )
        price = v.get("price", {})
        parts.append(
            f"Variant: {v.get('title', '')} - {status} - "
            f"{price.get('amount', '')} {price.get('currencyCode', '')} ({options})"
        )

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


def process_collection(collection: dict) -> list[dict]:
    """Convert a Shopify collection into documents."""
    parts = [f"Collection: {collection['title']}"]
    if collection.get("description"):
        parts.append(f"Description: {_strip_html(collection['description'])}")

    product_edges = collection.get("products", {}).get("edges", [])
    if product_edges:
        product_names = [e["node"]["title"] for e in product_edges]
        parts.append(f"Products in collection: {', '.join(product_names)}")

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


def process_page(page: dict) -> list[dict]:
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


def process_article(article: dict) -> list[dict]:
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


def process_policy(policy: dict) -> list[dict]:
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

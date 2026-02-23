import html as html_lib
import re

from config import settings

# Japanese character detection (Hiragana, Katakana, CJK Unified Ideographs)
_CJK_RE = re.compile(r"[\u3000-\u9fff\uf900-\ufaff]")


def _strip_html(raw) -> str:
    """Remove HTML tags and decode HTML entities."""
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", "", str(raw))
    return html_lib.unescape(text)


def _is_cjk_heavy(text: str) -> bool:
    """Return True if >=20% of characters are CJK (Japanese/Chinese)."""
    if not text:
        return False
    cjk_count = len(_CJK_RE.findall(text))
    return cjk_count / max(len(text), 1) > 0.2


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list:
    """Split text into overlapping chunks.

    Uses character-based chunking for CJK-heavy text (Japanese),
    and word-based chunking for Latin-script text (English).
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    if _is_cjk_heavy(text):
        return _chunk_by_chars(text, max_chars=1500, overlap_chars=200)

    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i : i + chunk_size]
        if chunk_words:
            chunks.append(" ".join(chunk_words))
    return chunks


def _chunk_by_chars(
    text: str, max_chars: int = 1500, overlap_chars: int = 200
) -> list:
    """Chunk CJK text by character count, splitting on paragraph/sentence
    boundaries to keep semantic coherence."""
    # Split into paragraphs first
    paragraphs = re.split(r"\n{2,}", text.strip())
    # Further split very long paragraphs on sentence boundaries
    segments: list[str] = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_chars:
            segments.append(para)
        else:
            # Split on Japanese sentence endings or newlines
            sentences = re.split(r"(?<=[。！？\n])", para)
            segments.extend(s.strip() for s in sentences if s.strip())

    if not segments:
        return [text] if text.strip() else []

    chunks: list[str] = []
    current = ""
    for seg in segments:
        if current and len(current) + len(seg) + 1 > max_chars:
            chunks.append(current)
            # Overlap: keep the tail of the current chunk
            if overlap_chars > 0 and len(current) > overlap_chars:
                current = current[-overlap_chars:] + "\n" + seg
            else:
                current = seg
        else:
            current = current + "\n" + seg if current else seg

    if current:
        chunks.append(current)

    return chunks if chunks else [text]


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
    """Convert a plain-text knowledge base file into documents.

    If the file contains ``===`` section separators, each section is
    chunked independently with a larger chunk window so that a single
    product / topic stays inside one chunk wherever possible.
    """
    from pathlib import Path

    path = Path(filepath)
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    title = path.stem.replace("_", " ").title()

    # Section-aware chunking for files with === separators
    if "\n===\n" in text or "\n===\n" in text.replace("\r\n", "\n"):
        return _process_sectioned_knowledge(text, title)

    metadata = {
        "type": "knowledge",
        "title": title,
        "url": "",
    }

    return [
        {"text": chunk, "metadata": metadata}
        for chunk in chunk_text(text)
    ]


def _process_sectioned_knowledge(text: str, base_title: str) -> list:
    """Process knowledge files with ``===`` section separators.

    Each section is chunked independently with a generous window so that
    a single product / topic fits in one chunk (typical wholesale product
    entries are 400-700 words EN / 1500-2500 chars JA).
    """
    sections = re.split(r"\n*={3,}\n*", text)
    docs: list[dict] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Use the first line as a section-specific title
        first_line = section.split("\n", 1)[0].strip()
        section_title = (
            f"{base_title} — {first_line}" if first_line else base_title
        )
        metadata = {"type": "knowledge", "title": section_title, "url": ""}

        # Larger chunk window to keep each product/section intact
        if _is_cjk_heavy(section):
            chunks = _chunk_by_chars(section, max_chars=4000, overlap_chars=200)
        else:
            words = section.split()
            if len(words) <= 1500:
                # Fits in one chunk — keep together
                chunks = [section]
            else:
                # Very long section — fall back to default chunking
                chunks = chunk_text(section)

        for chunk in chunks:
            # Prefix every chunk with the section title for better retrieval
            prefixed = f"[{section_title}]\n{chunk}"
            docs.append({"text": prefixed, "metadata": metadata})

    return docs


def process_knowledge_article(article: dict) -> list:
    """Convert a Supabase knowledge article into documents for embedding.

    Each chunk is prefixed with the article title so that every chunk
    carries context about its source document — critical for retrieval.
    HTML entities in content are decoded for clean embedding.
    """
    title = article.get("title", "")
    content = html_lib.unescape(article.get("content", "")).strip()
    if not content:
        return []

    metadata = {
        "type": "knowledge",
        "title": title,
        "url": "",
        "source": "supabase",
        "category": article.get("category", "general"),
        "language": article.get("language", "en"),
    }

    chunks = chunk_text(content)
    title_prefix = f"[{title}]\n" if title else ""

    return [
        {"text": title_prefix + chunk, "metadata": metadata}
        for chunk in chunks
    ]

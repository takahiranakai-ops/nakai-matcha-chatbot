"""Data ingestion script — fetches store data and builds vector embeddings."""

import asyncio
import sys

from services import shopify_client
from services.nvidia_client import get_embeddings
from pathlib import Path

from services.data_processor import (
    process_product,
    process_collection,
    process_page,
    process_article,
    process_policy,
    process_knowledge_file,
    process_knowledge_article,
)
from services.vector_store import VectorStore
from config import settings


async def run_ingestion(vector_store: VectorStore) -> int:
    """Ingest all store data into the vector store. Returns document count."""
    vector_store.clear()
    all_documents: list[dict] = []

    # 1. Products (Storefront API) — graceful failure
    try:
        print("Fetching products...")
        products = await shopify_client.fetch_products()
        for product in products:
            all_documents.extend(process_product(product))
        print(f"  -> {len(products)} products -> {len(all_documents)} chunks")
    except Exception as e:
        print(f"  -> Product fetch failed (non-critical): {e}")

    # 2. Collections (Storefront API) — graceful failure
    try:
        print("Fetching collections...")
        collections = await shopify_client.fetch_collections()
        before = len(all_documents)
        for collection in collections:
            all_documents.extend(process_collection(collection))
        print(f"  -> {len(collections)} collections -> {len(all_documents) - before} chunks")
    except Exception as e:
        print(f"  -> Collections fetch failed (non-critical): {e}")

    # 3. Pages (Admin API) — graceful failure
    try:
        print("Fetching pages...")
        pages = await shopify_client.fetch_pages()
        before = len(all_documents)
        for page in pages:
            all_documents.extend(process_page(page))
        print(f"  -> {len(pages)} pages -> {len(all_documents) - before} chunks")
    except Exception as e:
        print(f"  -> Pages fetch failed (non-critical): {e}")

    # 4. Blog articles (Admin API) — graceful failure
    try:
        print("Fetching blog articles...")
        articles = await shopify_client.fetch_blog_articles()
        before = len(all_documents)
        for article in articles:
            all_documents.extend(process_article(article))
        print(f"  -> {len(articles)} articles -> {len(all_documents) - before} chunks")
    except Exception as e:
        print(f"  -> Blog fetch failed (non-critical): {e}")

    # 5. Policies (Admin API) — graceful failure
    try:
        print("Fetching policies...")
        policies = await shopify_client.fetch_policies()
        before = len(all_documents)
        for policy in policies:
            all_documents.extend(process_policy(policy))
        print(f"  -> {len(policies)} policies -> {len(all_documents) - before} chunks")
    except Exception as e:
        print(f"  -> Policies fetch failed (non-critical): {e}")

    # 6. Custom knowledge base files (ALWAYS runs — no external dependency)
    knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"
    if knowledge_dir.exists():
        print("Loading custom knowledge base...")
        before = len(all_documents)
        for txt_file in sorted(knowledge_dir.glob("*.txt")):
            try:
                file_before = len(all_documents)
                all_documents.extend(process_knowledge_file(str(txt_file)))
                file_chunks = len(all_documents) - file_before
                print(f"    {txt_file.name}: {file_chunks} chunks")
            except Exception as e:
                print(f"    {txt_file.name}: FAILED ({e})")
        print(f"  -> {len(all_documents) - before} chunks from knowledge base")

    # 7. Supabase knowledge articles
    try:
        from services.supabase_client import list_articles, _is_configured
        if _is_configured():
            print("Loading Supabase knowledge articles...")
            before = len(all_documents)
            sb_articles = await list_articles(active_only=True)
            for sb_article in sb_articles:
                all_documents.extend(process_knowledge_article(sb_article))
            print(f"  -> {len(sb_articles)} articles -> {len(all_documents) - before} chunks from Supabase")
    except Exception as e:
        print(f"  -> Supabase knowledge fetch skipped: {e}")

    if not all_documents:
        print("No documents to ingest!")
        return 0

    # 8. Embed and store in batches (per-batch error handling)
    print(f"\nEmbedding {len(all_documents)} document chunks...")
    batch_size = 50
    embedded_count = 0
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i : i + batch_size]
        texts = [doc["text"] for doc in batch]
        try:
            embeddings = await get_embeddings(texts, input_type="passage")
            vector_store.add_documents(batch, embeddings)
            embedded_count += len(batch)
            print(f"  -> Batch {i // batch_size + 1}: {len(batch)} documents embedded")
        except Exception as e:
            print(f"  -> Batch {i // batch_size + 1} FAILED: {e}")

    total = vector_store.count()
    print(f"\nIngestion complete! {embedded_count}/{len(all_documents)} embedded. Total in store: {total}")
    return total


async def main():
    vs = VectorStore(settings.chroma_persist_dir)
    await run_ingestion(vs)


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    asyncio.run(main())

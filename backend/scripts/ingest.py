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
)
from services.vector_store import VectorStore
from config import settings


async def run_ingestion(vector_store: VectorStore) -> int:
    """Ingest all store data into the vector store. Returns document count."""
    vector_store.clear()
    all_documents: list[dict] = []

    # 1. Products (Storefront API)
    print("Fetching products...")
    products = await shopify_client.fetch_products()
    for product in products:
        all_documents.extend(process_product(product))
    print(f"  -> {len(products)} products -> {len(all_documents)} chunks")

    # 2. Collections (Storefront API)
    print("Fetching collections...")
    collections = await shopify_client.fetch_collections()
    before = len(all_documents)
    for collection in collections:
        all_documents.extend(process_collection(collection))
    print(f"  -> {len(collections)} collections -> {len(all_documents) - before} chunks")

    # 3. Pages (Admin API)
    print("Fetching pages...")
    pages = await shopify_client.fetch_pages()
    before = len(all_documents)
    for page in pages:
        all_documents.extend(process_page(page))
    print(f"  -> {len(pages)} pages -> {len(all_documents) - before} chunks")

    # 4. Blog articles (Admin API)
    print("Fetching blog articles...")
    articles = await shopify_client.fetch_blog_articles()
    before = len(all_documents)
    for article in articles:
        all_documents.extend(process_article(article))
    print(f"  -> {len(articles)} articles -> {len(all_documents) - before} chunks")

    # 5. Policies (Admin API)
    print("Fetching policies...")
    policies = await shopify_client.fetch_policies()
    before = len(all_documents)
    for policy in policies:
        all_documents.extend(process_policy(policy))
    print(f"  -> {len(policies)} policies -> {len(all_documents) - before} chunks")

    # 6. Custom knowledge base files
    knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"
    if knowledge_dir.exists():
        print("Loading custom knowledge base...")
        before = len(all_documents)
        for txt_file in sorted(knowledge_dir.glob("*.txt")):
            all_documents.extend(process_knowledge_file(str(txt_file)))
        print(f"  -> {len(all_documents) - before} chunks from knowledge base")

    if not all_documents:
        print("No documents to ingest!")
        return 0

    # 7. Embed and store in batches
    print(f"\nEmbedding {len(all_documents)} document chunks...")
    batch_size = 50
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i : i + batch_size]
        texts = [doc["text"] for doc in batch]
        embeddings = await get_embeddings(texts, input_type="passage")
        vector_store.add_documents(batch, embeddings)
        print(f"  -> Batch {i // batch_size + 1}: {len(batch)} documents embedded")

    total = vector_store.count()
    print(f"\nIngestion complete! Total documents: {total}")
    return total


async def main():
    vs = VectorStore(settings.chroma_persist_dir)
    await run_ingestion(vs)


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    asyncio.run(main())

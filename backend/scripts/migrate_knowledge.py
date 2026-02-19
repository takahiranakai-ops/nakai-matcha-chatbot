"""One-time migration: load existing .txt knowledge files into Supabase.

Usage: cd backend && python scripts/migrate_knowledge.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.supabase_client import create_article, _is_configured

CATEGORY_MAP = {
    "barista_guide": "brewing",
    "barista_guide_ja": "brewing",
    "matcha_advanced_faq": "faq",
    "matcha_basics_ja": "faq",
    "matcha_faq": "faq",
    "matcha_faq_ja": "faq",
    "matcha_powder_guide": "product",
    "matcha_science": "science",
    "matcha_vs_coffee": "science",
    "nakai_products": "product",
    "nakai_products_ja": "product",
    "revi_recipes": "recipe",
    "revi_recipes_ja": "recipe",
    "shipping_and_returns": "shipping",
    "shipping_and_returns_ja": "shipping",
    "water_science": "science",
}


async def migrate():
    if not _is_configured():
        print("Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
        return

    knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"
    for txt_file in sorted(knowledge_dir.glob("*.txt")):
        stem = txt_file.stem
        title = stem.replace("_", " ").title()
        content = txt_file.read_text(encoding="utf-8").strip()
        language = "ja" if stem.endswith("_ja") else "en"
        category = CATEGORY_MAP.get(stem, "general")

        print(f"Migrating: {stem} -> {title} [{language}, {category}]")
        result = await create_article(
            title=title,
            content=content,
            language=language,
            category=category,
            slug=stem,
        )
        if result:
            print(f"  -> Created: {result['id']}")
        else:
            print(f"  -> FAILED")


if __name__ == "__main__":
    asyncio.run(migrate())

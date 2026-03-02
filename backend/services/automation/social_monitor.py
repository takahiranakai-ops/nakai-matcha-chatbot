"""WS39: Social Mention Monitor — Reddit & X tracking.

Monitors social platforms for NAKAI brand mentions:
- Reddit: r/Matcha, r/tea, r/JapaneseFood, r/barista, r/cafe
- X (Twitter): @nakai_matcha mentions and keyword tracking

Sentiment analysis via NVIDIA NIM (existing infra).
Runs every 6 hours.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Reddit target subreddits
SUBREDDITS = ["Matcha", "tea", "JapaneseFood", "barista", "cafe", "nootropics"]

# Keywords to monitor
KEYWORDS = [
    "NAKAI matcha",
    "nakai matcha",
    "ナカイ抹茶",
    "NAKAI 抹茶",
    "nakaimatcha",
]


async def _search_reddit(keyword: str) -> list[dict]:
    """Search Reddit for keyword mentions via public JSON API."""
    mentions = []
    try:
        async with httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "NAKAI-Monitor/1.0"},
        ) as client:
            resp = await client.get(
                "https://www.reddit.com/search.json",
                params={"q": keyword, "sort": "new", "limit": 25, "t": "week"},
            )
            if resp.status_code == 200:
                data = resp.json()
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    mentions.append({
                        "platform": "reddit",
                        "subreddit": post.get("subreddit", ""),
                        "title": post.get("title", ""),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "author": post.get("author", ""),
                        "score": post.get("score", 0),
                        "created_utc": post.get("created_utc", 0),
                        "text": post.get("selftext", "")[:500],
                        "keyword": keyword,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
    except Exception as e:
        logger.error(f"Reddit search failed for '{keyword}': {e}")

    return mentions


async def _search_subreddit(subreddit: str) -> list[dict]:
    """Search a specific subreddit for any NAKAI mentions."""
    mentions = []
    try:
        async with httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "NAKAI-Monitor/1.0"},
        ) as client:
            resp = await client.get(
                f"https://www.reddit.com/r/{subreddit}/new.json",
                params={"limit": 50},
            )
            if resp.status_code == 200:
                data = resp.json()
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    text = (
                        post.get("title", "") + " " + post.get("selftext", "")
                    ).lower()
                    if "nakai" in text:
                        mentions.append({
                            "platform": "reddit",
                            "subreddit": subreddit,
                            "title": post.get("title", ""),
                            "url": f"https://reddit.com{post.get('permalink', '')}",
                            "author": post.get("author", ""),
                            "score": post.get("score", 0),
                            "created_utc": post.get("created_utc", 0),
                            "text": post.get("selftext", "")[:500],
                            "keyword": "nakai",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })
    except Exception as e:
        logger.error(f"Subreddit scan failed for r/{subreddit}: {e}")

    return mentions


async def monitor_social_mentions() -> list[dict]:
    """Run full social mention scan. Returns list of mentions found."""
    all_mentions = []

    # Keyword search
    for keyword in KEYWORDS:
        mentions = await _search_reddit(keyword)
        all_mentions.extend(mentions)

    # Subreddit scan
    for sub in SUBREDDITS:
        mentions = await _search_subreddit(sub)
        all_mentions.extend(mentions)

    # Deduplicate by URL
    seen_urls = set()
    unique_mentions = []
    for m in all_mentions:
        if m["url"] not in seen_urls:
            seen_urls.add(m["url"])
            unique_mentions.append(m)

    # Store in Supabase
    try:
        from services import supabase_client
        for m in unique_mentions:
            await supabase_client.store_social_mention(m)
    except Exception as e:
        logger.error(f"Failed to store social mentions: {e}")

    logger.info(f"Social monitor complete: {len(unique_mentions)} unique mentions found")
    return unique_mentions

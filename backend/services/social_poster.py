"""Social media auto-poster — posts to Twitter/X, Threads, LINE, and Reddit."""

import logging
from datetime import datetime, timezone

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def post_to_twitter(text: str) -> dict:
    """Post a tweet using Twitter API v2 with OAuth 1.0a."""
    if not all([
        settings.twitter_api_key,
        settings.twitter_api_secret,
        settings.twitter_access_token,
        settings.twitter_access_secret,
    ]):
        logger.warning("[TWITTER] API keys not configured — skipping")
        return {"status": "skipped", "reason": "not_configured"}

    try:
        import tweepy

        client = tweepy.Client(
            consumer_key=settings.twitter_api_key,
            consumer_secret=settings.twitter_api_secret,
            access_token=settings.twitter_access_token,
            access_token_secret=settings.twitter_access_secret,
        )
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        logger.info(f"[TWITTER] Posted tweet: {tweet_id}")
        return {"status": "success", "tweet_id": tweet_id}
    except Exception as e:
        logger.error(f"[TWITTER] Post failed: {e}")
        return {"status": "error", "error": str(e)}


async def post_to_threads(text: str) -> dict:
    """Post to Threads using Meta Graph API."""
    if not settings.threads_access_token or not settings.threads_user_id:
        logger.warning("[THREADS] Access token or user ID not configured — skipping")
        return {"status": "skipped", "reason": "not_configured"}

    try:
        base = "https://graph.threads.net/v1.0"
        headers = {"Authorization": f"Bearer {settings.threads_access_token}"}

        # Step 1: Create media container
        async with httpx.AsyncClient(timeout=30) as client:
            create_resp = await client.post(
                f"{base}/{settings.threads_user_id}/threads",
                headers=headers,
                json={"media_type": "TEXT", "text": text},
            )
            create_resp.raise_for_status()
            container_id = create_resp.json()["id"]

            # Step 2: Publish
            publish_resp = await client.post(
                f"{base}/{settings.threads_user_id}/threads_publish",
                headers=headers,
                json={"creation_id": container_id},
            )
            publish_resp.raise_for_status()
            post_id = publish_resp.json()["id"]

        logger.info(f"[THREADS] Posted: {post_id}")
        return {"status": "success", "post_id": post_id}
    except Exception as e:
        logger.error(f"[THREADS] Post failed: {e}")
        return {"status": "error", "error": str(e)}


async def post_to_line(text: str) -> dict:
    """Broadcast message to all LINE followers using Messaging API."""
    if not settings.line_channel_access_token:
        logger.warning("[LINE] Channel access token not configured — skipping")
        return {"status": "skipped", "reason": "not_configured"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.line.me/v2/bot/message/broadcast",
                headers={
                    "Authorization": f"Bearer {settings.line_channel_access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "messages": [{"type": "text", "text": text}],
                },
            )
            resp.raise_for_status()

        logger.info("[LINE] Broadcast sent successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"[LINE] Broadcast failed: {e}")
        return {"status": "error", "error": str(e)}


async def post_to_reddit(text: str) -> dict:
    """Post to Reddit using PRAW. Text format: 'TITLE: ... BODY: ...'"""
    if not all([
        settings.reddit_client_id,
        settings.reddit_client_secret,
        settings.reddit_username,
        settings.reddit_password,
    ]):
        logger.warning("[REDDIT] API credentials not configured — skipping")
        return {"status": "skipped", "reason": "not_configured"}

    try:
        import praw

        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            username=settings.reddit_username,
            password=settings.reddit_password,
            user_agent=settings.reddit_user_agent,
        )

        # Parse title and body from generated content
        title = text
        body = ""
        if "TITLE:" in text and "BODY:" in text:
            parts = text.split("BODY:", 1)
            title = parts[0].replace("TITLE:", "").strip()
            body = parts[1].strip()

        # Rotate through subreddits (1 per day based on day-of-year)
        subreddits = ["Matcha", "tea", "JapaneseFood", "cafe", "barista"]
        day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
        target_sub = subreddits[day_of_year % len(subreddits)]

        subreddit = reddit.subreddit(target_sub)
        submission = subreddit.submit(title=title, selftext=body)
        logger.info(f"[REDDIT] Posted to r/{target_sub}: {submission.id}")
        return {
            "status": "success",
            "post_id": submission.id,
            "subreddit": target_sub,
            "url": f"https://reddit.com{submission.permalink}",
        }
    except Exception as e:
        logger.error(f"[REDDIT] Post failed: {e}")
        return {"status": "error", "error": str(e)}


async def post_all(content: dict[str, str]) -> dict:
    """Post to all configured platforms and log results.

    Args:
        content: Dict with keys 'twitter', 'threads', 'line', 'topic'

    Returns:
        Dict with results for each platform
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": content.get("topic", "unknown"),
    }

    platforms = ["twitter", "threads", "line"]
    results["twitter"] = await post_to_twitter(content.get("twitter", ""))
    results["threads"] = await post_to_threads(content.get("threads", ""))
    results["line"] = await post_to_line(content.get("line", ""))

    # Post to Reddit if content was generated for it
    if "reddit" in content:
        platforms.append("reddit")
        results["reddit"] = await post_to_reddit(content["reddit"])

    # Log to Supabase
    await _log_to_supabase(results, content)

    success_count = sum(1 for k in platforms if results.get(k, {}).get("status") == "success")
    skip_count = sum(1 for k in platforms if results.get(k, {}).get("status") == "skipped")
    total = len(platforms)
    logger.info(f"[SOCIAL] Posted to {success_count}/{total} platforms ({skip_count} skipped)")

    return results


async def _log_to_supabase(results: dict, content: dict):
    """Log posting results to Supabase for tracking."""
    if not settings.supabase_url or not settings.supabase_service_key:
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{settings.supabase_url}/rest/v1/daily_tips_log",
                headers={
                    "apikey": settings.supabase_service_key,
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json={
                    "topic": results.get("topic", ""),
                    "twitter_status": results.get("twitter", {}).get("status", ""),
                    "threads_status": results.get("threads", {}).get("status", ""),
                    "line_status": results.get("line", {}).get("status", ""),
                    "twitter_text": content.get("twitter", ""),
                    "threads_text": content.get("threads", ""),
                    "line_text": content.get("line", ""),
                    "posted_at": results.get("timestamp", ""),
                },
            )
    except Exception as e:
        logger.warning(f"[DAILY_TIPS] Supabase logging failed (non-critical): {e}")

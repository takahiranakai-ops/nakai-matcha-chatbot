"""B2B Email Hunter — Discovers email addresses for café leads.

Virtual Team Members #9-12: Email Hunters.
Strategy: Website scraping → Hunter.io API → pattern generation.
"""

import ipaddress
import logging
import re
from urllib.parse import urlparse

import httpx

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
)

# Skip these common non-business emails
SKIP_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "example.com", "sentry.io", "wixpress.com", "squarespace.com",
    "shopify.com", "wordpress.com", "google.com", "facebook.com",
}


async def find_emails_for_lead(lead: dict) -> list[dict]:
    """Find email addresses for a lead. Returns list of saved contacts."""
    lead_id = lead["id"]
    website = lead.get("website", "")
    name = lead.get("name", "")
    results = []

    # Step 1: Scrape website for emails
    if website:
        scraped = await _scrape_website_emails(website)
        for email in scraped:
            saved = await _save_contact(lead_id, email, "website")
            if saved:
                results.append(saved)

    # Step 2: Hunter.io domain search
    if website and settings.hunter_io_api_key and not results:
        domain = _extract_domain(website)
        if domain:
            hunter_results = await _hunter_domain_search(domain)
            for item in hunter_results:
                saved = await _save_contact(
                    lead_id, item["email"], "hunter", item.get("name", ""),
                    item.get("position", ""),
                )
                if saved:
                    results.append(saved)

    # Step 3: Generate common patterns as fallback
    if website and not results:
        domain = _extract_domain(website)
        if domain:
            patterns = _generate_email_patterns(domain)
            for email in patterns:
                saved = await _save_contact(lead_id, email, "pattern")
                if saved:
                    results.append(saved)

    logger.info(f"[B2B] Found {len(results)} emails for '{name}'")
    return results


async def find_emails_batch(leads: list[dict], max_leads: int = 20) -> int:
    """Process a batch of leads. Returns total emails found."""
    total = 0
    for lead in leads[:max_leads]:
        contacts = await find_emails_for_lead(lead)
        total += len(contacts)
    return total


def _is_safe_url(url: str) -> bool:
    """Validate URL is safe to fetch (no SSRF)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Block private/internal IPs
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            pass  # hostname is not an IP — that's fine
        return True
    except Exception:
        return False


async def _scrape_website_emails(url: str) -> list[str]:
    """Scrape emails from a website's main pages."""
    emails = set()

    # Normalize URL
    if not url.startswith("http"):
        url = f"https://{url}"

    if not _is_safe_url(url):
        logger.warning(f"[B2B] Blocked unsafe URL: {url}")
        return []

    pages_to_check = [url]
    # Also check common contact pages
    base = url.rstrip("/")
    for path in ["/contact", "/about", "/about-us", "/contact-us"]:
        pages_to_check.append(base + path)

    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "NAKAI-B2B-Research/1.0"},
        ) as client:
            for page_url in pages_to_check:
                try:
                    resp = await client.get(page_url)
                    if resp.status_code == 200:
                        found = EMAIL_REGEX.findall(resp.text)
                        for email in found:
                            email = email.lower().strip()
                            domain = email.split("@")[1]
                            if domain not in SKIP_DOMAINS:
                                emails.add(email)
                except Exception as e:
                    logger.debug("[B2B] Failed to scrape %s: %s", page_url, e)
                    continue

    except Exception as e:
        logger.debug(f"[B2B] Website scraping failed for {url}: {e}")

    return list(emails)[:5]


async def _hunter_domain_search(domain: str) -> list[dict]:
    """Search Hunter.io for emails at a domain."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.hunter.io/v2/domain-search",
                params={
                    "domain": domain,
                    "api_key": settings.hunter_io_api_key,
                    "limit": 5,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "email": e.get("value", ""),
                    "name": f"{e.get('first_name', '')} {e.get('last_name', '')}".strip(),
                    "position": e.get("position", ""),
                }
                for e in data.get("data", {}).get("emails", [])
                if e.get("value")
            ]
    except Exception as e:
        logger.debug(f"[B2B] Hunter.io search failed for {domain}: {e}")
        return []


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    url = url.lower().replace("https://", "").replace("http://", "")
    url = url.split("/")[0]
    url = url.replace("www.", "")
    return url


def _generate_email_patterns(domain: str) -> list[str]:
    """Generate common email patterns for a domain."""
    return [
        f"info@{domain}",
        f"hello@{domain}",
        f"contact@{domain}",
    ]


async def _save_contact(
    lead_id: str, email: str, source: str,
    name: str = "", role: str = "",
) -> dict | None:
    """Save a contact to Supabase."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()

    # Check unsubscribe list
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_unsubscribes",
            headers=supabase_client._HEADERS,
            params={"email": f"eq.{email}", "limit": "1"},
        )
        if resp.json():
            logger.debug(f"[B2B] Skipping unsubscribed email: {email}")
            return None
    except Exception as e:
        logger.warning("[B2B] Unsubscribe check failed for %s: %s", email, e)
        return None

    try:
        client = supabase_client._get_client()
        resp = await client.post(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers={
                **supabase_client._HEADERS,
                "Prefer": "return=representation,resolution=ignore-duplicates",
            },
            json={
                "lead_id": lead_id,
                "email": email,
                "name": name,
                "role": role or "general",
                "source": source,
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.debug(f"[B2B] Contact save failed: {e}")
        return None

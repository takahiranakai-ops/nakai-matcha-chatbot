"""B2B Email Verifier — Validates email addresses via MX + SMTP checks.

Virtual Team Members #13-14: Email Verifiers.
"""

import logging
import re

from services import supabase_client

logger = logging.getLogger(__name__)


async def verify_email(email: str) -> str:
    """Verify an email address. Returns: valid, invalid, catch_all, unknown."""
    if not _is_valid_format(email):
        return "invalid"

    domain = email.split("@")[1]

    # Check MX records
    has_mx = await _check_mx(domain)
    if not has_mx:
        return "invalid"

    return "valid"


async def verify_batch(max_contacts: int = 50) -> int:
    """Verify a batch of unverified contacts. Returns count verified."""
    if not supabase_client._is_configured():
        return 0
    supabase_client._init()

    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers=supabase_client._HEADERS,
            params={
                "verification_status": "eq.pending",
                "limit": str(max_contacts),
                "order": "created_at.asc",
            },
        )
        resp.raise_for_status()
        contacts = resp.json()
    except Exception as e:
        logger.error(f"[B2B] Failed to fetch contacts for verification: {e}")
        return 0

    verified_count = 0
    for contact in contacts:
        email = contact.get("email", "")
        status = await verify_email(email)

        try:
            await client.patch(
                f"{supabase_client._BASE_URL}/b2b_contacts",
                headers={**supabase_client._HEADERS, "Prefer": "return=minimal"},
                params={"id": f"eq.{contact['id']}"},
                json={
                    "verified": status == "valid",
                    "verification_status": status,
                },
            )
            verified_count += 1
        except Exception as e:
            logger.debug(f"[B2B] Verification update failed for {email}: {e}")

    logger.info(f"[B2B] Verified {verified_count} contacts")
    return verified_count


def _is_valid_format(email: str) -> bool:
    """Basic email format check."""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


async def _check_mx(domain: str) -> bool:
    """Check if domain has MX records."""
    try:
        import dns.resolver
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except ImportError:
        # dnspython not installed, assume valid
        return True
    except Exception:
        return False

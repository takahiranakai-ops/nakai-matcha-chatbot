"""B2B Lead Importer — Import cafés from Excel/CSV files."""

import csv
import io
import logging
from typing import BinaryIO

from services import supabase_client

logger = logging.getLogger(__name__)

# Common column name mappings
COLUMN_MAP = {
    # name
    "name": "name", "cafe_name": "name", "business_name": "name",
    "company": "name", "store": "name", "shop": "name",
    # email
    "email": "email", "e-mail": "email", "contact_email": "email",
    "email_address": "email",
    # city
    "city": "city", "town": "city", "location": "city",
    # state
    "state": "state", "province": "state", "region": "state",
    # country
    "country": "country", "nation": "country",
    # website
    "website": "website", "url": "website", "web": "website",
    "site": "website", "homepage": "website",
    # phone
    "phone": "phone", "telephone": "phone", "tel": "phone",
    "phone_number": "phone",
    # address
    "address": "address", "street": "address", "full_address": "address",
    # type
    "type": "cafe_type", "cafe_type": "cafe_type", "category": "cafe_type",
    "business_type": "cafe_type",
    # notes
    "notes": "notes", "comments": "notes", "description": "notes",
}


async def import_excel(file_content: bytes, filename: str) -> dict:
    """Import leads from an Excel (.xlsx) file.

    Returns: {"imported": count, "skipped": count, "errors": [...]}
    """
    try:
        import openpyxl
    except ImportError:
        return {"imported": 0, "skipped": 0, "errors": ["openpyxl not installed"]}

    wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 2:
        return {"imported": 0, "skipped": 0, "errors": ["File has no data rows"]}

    headers = [str(h).strip().lower().replace(" ", "_") if h else "" for h in rows[0]]
    return await _process_rows(headers, rows[1:])


async def import_csv(file_content: bytes) -> dict:
    """Import leads from a CSV file."""
    text = file_content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if len(rows) < 2:
        return {"imported": 0, "skipped": 0, "errors": ["File has no data rows"]}

    headers = [h.strip().lower().replace(" ", "_") for h in rows[0]]
    return await _process_rows(headers, rows[1:])


async def _process_rows(headers: list[str], rows: list) -> dict:
    """Process rows and insert into Supabase."""
    # Map columns
    col_indices: dict[str, int] = {}
    for i, header in enumerate(headers):
        mapped = COLUMN_MAP.get(header)
        if mapped and mapped not in col_indices:
            col_indices[mapped] = i

    if "name" not in col_indices:
        return {"imported": 0, "skipped": 0, "errors": ["No 'name' column found"]}

    imported = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(rows, start=2):
        try:
            row_vals = list(row)
            name_idx = col_indices["name"]
            name = str(row_vals[name_idx]).strip() if name_idx < len(row_vals) and row_vals[name_idx] else ""

            if not name:
                skipped += 1
                continue

            lead_data = {
                "name": name,
                "source": "import",
                "status": "new",
                "lead_score": 0,
            }

            for field, idx in col_indices.items():
                if field == "name" or field == "email":
                    continue
                if idx < len(row_vals) and row_vals[idx]:
                    lead_data[field] = str(row_vals[idx]).strip()

            # Insert lead
            saved = await _insert_lead(lead_data)
            if not saved:
                skipped += 1
                continue

            # If email column exists, create contact
            if "email" in col_indices:
                email_idx = col_indices["email"]
                if email_idx < len(row_vals) and row_vals[email_idx]:
                    email = str(row_vals[email_idx]).strip()
                    if "@" in email:
                        await _insert_contact(saved["id"], email)

            imported += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {e}")
            if len(errors) > 20:
                errors.append("... (truncated)")
                break

    logger.info(f"[B2B] Import complete: {imported} imported, {skipped} skipped")
    return {"imported": imported, "skipped": skipped, "errors": errors}


async def _insert_lead(data: dict) -> dict | None:
    """Insert a single lead."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.post(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers={**supabase_client._HEADERS, "Prefer": "return=representation"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.debug(f"[B2B] Lead insert failed: {e}")
        return None


async def _insert_contact(lead_id: str, email: str) -> dict | None:
    """Insert a contact for a lead."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
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
                "source": "import",
                "role": "general",
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.debug(f"[B2B] Contact insert failed: {e}")
        return None

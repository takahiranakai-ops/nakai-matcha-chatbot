"""B2B Lead Researcher — Discovers cafés via Google Places API.

Virtual Team Members #1-8: Lead Researchers & New Café Scouts.
Searches across US and EU regions, including newly opened cafés.
"""

import logging
from datetime import datetime, timezone

import httpx

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

# 8 regions with key cities
REGIONS: dict[str, dict] = {
    "us_west": {
        "label": "US West",
        "cities": [
            "San Francisco, CA", "Los Angeles, CA", "Seattle, WA", "Portland, OR",
            "San Diego, CA", "Denver, CO", "Phoenix, AZ", "Las Vegas, NV",
            "Salt Lake City, UT", "Honolulu, HI", "Sacramento, CA", "Oakland, CA",
        ],
    },
    "us_east": {
        "label": "US East",
        "cities": [
            "New York, NY", "Boston, MA", "Philadelphia, PA", "Washington, DC",
            "Miami, FL", "Atlanta, GA", "Charlotte, NC", "Baltimore, MD",
            "Pittsburgh, PA", "Providence, RI", "Brooklyn, NY", "Cambridge, MA",
        ],
    },
    "us_south": {
        "label": "US South",
        "cities": [
            "Austin, TX", "Dallas, TX", "Houston, TX", "Nashville, TN",
            "New Orleans, LA", "San Antonio, TX", "Charleston, SC", "Savannah, GA",
            "Raleigh, NC", "Tampa, FL", "Jacksonville, FL", "Richmond, VA",
        ],
    },
    "us_midwest": {
        "label": "US Midwest",
        "cities": [
            "Chicago, IL", "Minneapolis, MN", "Detroit, MI", "Milwaukee, WI",
            "Columbus, OH", "Indianapolis, IN", "Kansas City, MO", "St. Louis, MO",
            "Cincinnati, OH", "Madison, WI", "Ann Arbor, MI", "Cleveland, OH",
        ],
    },
    "eu_uk": {
        "label": "EU UK & Ireland",
        "cities": [
            "London, UK", "Edinburgh, UK", "Manchester, UK", "Bristol, UK",
            "Dublin, Ireland", "Glasgow, UK", "Brighton, UK", "Oxford, UK",
            "Cambridge, UK", "Bath, UK", "Liverpool, UK", "Belfast, UK",
        ],
    },
    "eu_central": {
        "label": "EU Central",
        "cities": [
            "Paris, France", "Berlin, Germany", "Amsterdam, Netherlands",
            "Munich, Germany", "Brussels, Belgium", "Vienna, Austria",
            "Zurich, Switzerland", "Hamburg, Germany", "Prague, Czech Republic",
            "Frankfurt, Germany", "Cologne, Germany", "Lyon, France",
        ],
    },
    "eu_nordic": {
        "label": "EU Nordic",
        "cities": [
            "Stockholm, Sweden", "Copenhagen, Denmark", "Oslo, Norway",
            "Helsinki, Finland", "Gothenburg, Sweden", "Malmö, Sweden",
            "Aarhus, Denmark", "Bergen, Norway", "Turku, Finland", "Reykjavik, Iceland",
        ],
    },
    "eu_med": {
        "label": "EU Mediterranean",
        "cities": [
            "Barcelona, Spain", "Madrid, Spain", "Milan, Italy", "Rome, Italy",
            "Lisbon, Portugal", "Athens, Greece", "Florence, Italy", "Valencia, Spain",
            "Porto, Portugal", "Naples, Italy", "Seville, Spain", "Marseille, France",
        ],
    },
}

SEARCH_KEYWORDS = [
    "specialty coffee shop",
    "matcha cafe",
    "artisan cafe",
    "third wave coffee",
    "organic cafe",
    "tea house",
]


async def search_cafes_in_city(city: str, keyword: str, region: str) -> list[dict]:
    """Search for cafés in a city using Google Places API.

    Returns list of leads added/updated.
    """
    if not settings.google_places_api_key:
        logger.warning("Google Places API key not configured")
        return []

    results = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "X-Goog-Api-Key": settings.google_places_api_key,
                    "X-Goog-FieldMask": (
                        "places.id,places.displayName,places.formattedAddress,"
                        "places.websiteUri,places.nationalPhoneNumber,"
                        "places.types,places.googleMapsUri"
                    ),
                },
                json={
                    "textQuery": f"{keyword} in {city}",
                    "maxResultCount": 20,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        for place in data.get("places", []):
            place_id = place.get("id", "")
            name = place.get("displayName", {}).get("text", "")
            if not name:
                continue

            # Determine country from city string
            country = "US"
            for eu_region in ("eu_uk", "eu_central", "eu_nordic", "eu_med"):
                if region == eu_region:
                    country = "EU"
                    break

            # Parse city/state from formatted address
            address = place.get("formattedAddress", "")
            parts = city.split(", ")
            city_name = parts[0] if parts else city
            state = parts[1] if len(parts) > 1 else ""

            lead_data = {
                "name": name,
                "address": address,
                "city": city_name,
                "state": state,
                "country": country,
                "region": region,
                "website": place.get("websiteUri", ""),
                "phone": place.get("nationalPhoneNumber", ""),
                "google_place_id": place_id,
                "cafe_type": _classify_cafe(place.get("types", [])),
                "status": "new",
                "lead_score": 0,
                "source": "google_places",
            }

            saved = await _upsert_lead(lead_data)
            if saved:
                results.append(saved)

        logger.info(f"[B2B] Found {len(results)} cafés for '{keyword}' in {city}")

    except Exception as e:
        logger.error(f"[B2B] Google Places search failed for {city}: {e}")

    return results


async def search_new_openings(city: str, region: str) -> list[dict]:
    """Search specifically for newly opened cafés."""
    return await search_cafes_in_city(city, "new coffee shop opened recently", region)


async def search_region(region_key: str, max_cities: int = 3, max_keywords: int = 3) -> list[dict]:
    """Search cities in a region with multiple keywords for higher volume."""
    region = REGIONS.get(region_key)
    if not region:
        return []

    day = datetime.now(timezone.utc).timetuple().tm_yday
    cities = region["cities"]
    start = (day * max_cities) % len(cities)
    selected = [cities[(start + i) % len(cities)] for i in range(max_cities)]

    # Use multiple keywords per city for more results
    kw_start = day % len(SEARCH_KEYWORDS)
    keywords = [SEARCH_KEYWORDS[(kw_start + i) % len(SEARCH_KEYWORDS)] for i in range(max_keywords)]

    all_results = []
    for city in selected:
        for keyword in keywords:
            results = await search_cafes_in_city(city, keyword, region_key)
            all_results.extend(results)

    return all_results


async def _upsert_lead(data: dict) -> dict | None:
    """Insert or update a lead by google_place_id."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        # Check for existing by google_place_id
        if data.get("google_place_id"):
            resp = await client.get(
                f"{supabase_client._BASE_URL}/b2b_leads",
                headers=supabase_client._HEADERS,
                params={
                    "google_place_id": f"eq.{data['google_place_id']}",
                    "limit": "1",
                },
            )
            existing = resp.json()
            if existing:
                return existing[0]

        resp = await client.post(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers={**supabase_client._HEADERS, "Prefer": "return=representation"},
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.debug(f"[B2B] Lead upsert failed: {e}")
        return None


def _classify_cafe(types: list[str]) -> str:
    """Classify café type from Google Places types."""
    type_set = set(types)
    if "bakery" in type_set:
        return "bakery"
    if "restaurant" in type_set:
        return "restaurant"
    if "lodging" in type_set or "hotel" in type_set:
        return "hotel"
    if "bar" in type_set:
        return "bar"
    return "specialty"

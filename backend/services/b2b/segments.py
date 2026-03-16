"""B2B Segment Definitions — Cafe, Luxury Hotel, Fine Dining.

Centralizes search keywords, Google Places type mapping,
follow-up delays, and UI metadata for each business segment.
"""

SEGMENTS: dict[str, dict] = {
    "cafe": {
        "label": "カフェ",
        "label_en": "Cafés",
        "icon": "coffee",
        "keywords": [
            "specialty coffee shop",
            "matcha cafe",
            "artisan cafe",
            "third wave coffee",
            "organic cafe",
            "tea house",
        ],
        "place_types": ["cafe", "bakery", "bar"],
        "delays": [0, 5, 7],
    },
    "luxury_hotel": {
        "label": "高級ホテル",
        "label_en": "Luxury Hotels",
        "icon": "building",
        "keywords": [
            "luxury hotel",
            "boutique hotel",
            "5 star hotel",
            "premium resort",
            "design hotel",
        ],
        "place_types": ["lodging", "hotel"],
        "delays": [0, 7, 14],
    },
    "fine_dining": {
        "label": "高級レストラン",
        "label_en": "Fine Dining",
        "icon": "tools-kitchen-2",
        "keywords": [
            "fine dining restaurant",
            "michelin restaurant",
            "upscale restaurant",
            "omakase restaurant",
            "tasting menu restaurant",
        ],
        "place_types": ["restaurant"],
        "delays": [0, 5, 10],
    },
}

SEGMENT_IDS = list(SEGMENTS.keys())


def classify_segment(google_types: list[str]) -> str:
    """Map Google Places types to a segment name."""
    type_set = set(google_types)
    for seg_id, seg in SEGMENTS.items():
        if type_set & set(seg["place_types"]):
            return seg_id
    return "cafe"


def get_segment_delays(segment: str) -> list[int]:
    """Return [step1_delay, step2_delay, step3_delay] for a segment."""
    seg = SEGMENTS.get(segment)
    if seg:
        return seg["delays"]
    return [0, 5, 7]

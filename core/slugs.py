import re
import unicodedata
from datetime import datetime, timezone


def normalize_str(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    return value


def slugify_trip(title: str) -> str:
    normalized_title = normalize_str(title)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized_title)
    if not slug:
        slug = f"trip-{int(datetime.now(timezone.utc).timestamp())}"
    return slug.strip("-").lower()

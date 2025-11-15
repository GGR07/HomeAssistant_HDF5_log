from datetime import datetime, timezone

def utc_now_z() -> str:
    """Return ISO-8601 UTC timestamp with Z suffix (timezone-aware)."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

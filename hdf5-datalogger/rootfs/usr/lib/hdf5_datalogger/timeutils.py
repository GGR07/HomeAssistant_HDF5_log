from datetime import datetime, timezone

def utc_now_z() -> str:
  """
  Ritorna timestamp ISO-8601 UTC con suffisso 'Z'.
  """
  return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

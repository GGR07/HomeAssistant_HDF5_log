from datetime import datetime, timezone, date

def utc_now_z() -> str:
    """
    Ritorna timestamp ISO-8601 UTC con suffisso 'Z'.
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def today_str_local() -> str:
    """
    Data odierna in formato YYYY-MM-DD (ora locale del container).
    """
    return date.today().isoformat()

from collections import defaultdict
from .constants import PRESET_DOMAINS, DOMAIN_CORRECTIONS

def domain_of(entity_id: str) -> str:
    return entity_id.split(".", 1)[0].lower() if "." in entity_id else "unknown"

def normalize_domain(d: str) -> str:
    if not d:
        return ""
    d = str(d).strip().lower()
    return DOMAIN_CORRECTIONS.get(d, d)

def discover_available_domains(states: list) -> set:
    s = set()
    for st in states:
        s.add(domain_of(st.get("entity_id", "")))
    return s

def build_domains_from_options(opts: dict, available_domains: set) -> tuple[set, list]:
    """
    Ritorna (selected_domains, warnings)
    - selected_domains: set (vuoto = include tutti)
    - warnings: lista di stringhe da mostrare nel report
    """
    warnings = []
    mode = (opts.get("domain_mode") or "presets").strip().lower()

    if mode == "all":
        return set(), warnings  # set vuoto => include tutti

    selected = set()

    if mode == "presets":
        presets = opts.get("domain_presets") or []
        for p in presets:
            key = str(p).strip().lower()
            if key in PRESET_DOMAINS:
                selected |= PRESET_DOMAINS[key]
            else:
                warnings.append(f"Unknown preset: {p}")
    elif mode == "custom":
        for d in (opts.get("domains_include") or []):
            nd = normalize_domain(d)
            if nd:
                selected.add(nd)
    else:
        warnings.append(f"Unknown domain_mode: {mode}. Using 'all'.")
        return set(), warnings

    # exclude sempre applicato
    for d in (opts.get("domains_exclude") or []):
        nd = normalize_domain(d)
        if nd in selected:
            selected.discard(nd)

    # strict: scarta domini non presenti realmente
    if selected:
        if opts.get("strict_domains", True):
            unknown = sorted([d for d in selected if d not in available_domains])
            if unknown:
                warnings.append("Strict mode: removed unknown domains -> " + ", ".join(unknown))
            selected = {d for d in selected if d in available_domains}
        if not selected:
            warnings.append("Selected domains empty after filtering. Falling back to (all).")
            return set(), warnings

    return selected, warnings

def group_states_by_domain(states: list, selected_domains: set) -> dict:
    grouped = defaultdict(list)
    for st in states:
        d = domain_of(st.get("entity_id", ""))
        if selected_domains and d not in selected_domains:
            continue
        grouped[d].append(st)
    return grouped

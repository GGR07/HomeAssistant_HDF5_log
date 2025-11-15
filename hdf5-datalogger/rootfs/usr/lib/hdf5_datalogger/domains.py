from collections import defaultdict
from .constants import DOMAIN_FLAGS

def domain_of(entity_id: str) -> str:
    return entity_id.split(".", 1)[0].lower() if "." in entity_id else "unknown"

def normalize_domain(d: str) -> str:
    if not d:
        return ""
    d = str(d).strip().lower()
    corrections = {
        "sensors": "sensor",
        "binary_sensors": "binary_sensor",
        "lights": "light",
        "switches": "switch",
        "binanry_sensor": "binary_sensor",
        "binanry_sensors": "binary_sensor",
    }
    return corrections.get(d, d)

def discover_available_domains(states: list) -> set:
    s = set()
    for st in states:
        s.add(domain_of(st.get("entity_id", "")))
    return s

def build_included_domains(opts: dict, available_domains: set) -> set:
    selected = set()

    # dai flag booleani
    for flag, dom in DOMAIN_FLAGS.items():
        if opts.get(flag, False):
            selected.add(dom)

    # extra manuali
    for d in (opts.get("include_domains_extra", []) or []):
        nd = normalize_domain(d)
        if nd:
            selected.add(nd)

    # se nulla selezionato => include tutti (set vuoto indica "tutti")
    if not selected:
        return set()

    # tieni solo domini presenti (evita report vuoti)
    if available_domains:
        return {d for d in selected if d in available_domains}
    return selected

def group_states_by_domain(states: list, selected_domains: set) -> dict:
    grouped = defaultdict(list)
    for st in states:
        d = domain_of(st.get("entity_id", ""))
        if selected_domains and d not in selected_domains:
            continue
        grouped[d].append(st)
    return grouped

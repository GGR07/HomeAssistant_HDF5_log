from collections import defaultdict

def domain_of(entity_id: str) -> str:
  if not entity_id or "." not in entity_id:
    return "unknown"
  return entity_id.split(".", 1)[0].lower()

def discover_available_domains(states: list) -> set:
  s = set()
  for st in states:
    eid = st.get("entity_id", "")
    s.add(domain_of(eid))
  return s

def build_included_domains(include_domains_raw: list, available_domains: set):
  """
  Ritorna (selected_domains, warnings):

  - selected_domains: set di domini da includere.
      * set vuoto => includi tutti (none filter).
  - warnings: lista di stringhe da mostrare nel report.
  """
  warnings = []
  if not include_domains_raw:
    # Nessun filtro di dominio richiesto
    return set(), warnings

  normalized = {str(d).strip().lower() for d in include_domains_raw if str(d).strip()}
  if not normalized:
    return set(), warnings

  unknown = sorted([d for d in normalized if d not in available_domains])
  effective = normalized & available_domains

  if unknown:
    warnings.append("Unknown domains in include_domains (ignored): " + ", ".join(unknown))

  if not effective:
    warnings.append("No domains from include_domains matched available; falling back to all.")
    return set(), warnings  # set vuoto => all

  return effective, warnings

def group_states_by_domain(states: list, selected_domains: set) -> dict:
  grouped = defaultdict(list)
  for st in states:
    eid = st.get("entity_id", "")
    d = domain_of(eid)
    if selected_domains and d not in selected_domains:
      continue
    grouped[d].append(st)
  return grouped

import json
from .timeutils import utc_now_z

def _format_state_lines_all_attrs(state: dict) -> list:
  lines = []
  entity_id = state.get("entity_id", "unknown")
  state_val = state.get("state", "unknown")
  attrs = state.get("attributes", {}) or {}

  friendly = attrs.get("friendly_name")

  lines.append(f"- {entity_id}")
  lines.append(f"  state: {state_val}")
  if friendly:
    lines.append(f"  name: {friendly}")

  for key in sorted(attrs.keys()):
    if key == "friendly_name":
      continue
    val = attrs[key]
    if isinstance(val, (dict, list)):
      try:
        val_str = json.dumps(val, ensure_ascii=False, separators=(",", ":"))
      except Exception:
        val_str = str(val)
    else:
      val_str = str(val)
    lines.append(f"  {key}: {val_str}")

  return lines

def write_report(
  output_path: str,
  grouped: dict,
  max_entities: int,
  available_domains: set,
  included_domains_effective: set,
  include_domains_raw: list,
  filter_stats: dict,
  domain_warnings: list,
):
  ts = utc_now_z()
  with open(output_path, "w", encoding="utf-8") as f:
    f.write("===== HOME ASSISTANT STATES REPORT =====\n")
    f.write(f"Generated at: {ts}\n\n")

    # Info domini
    if included_domains_effective:
      f.write("Included domains (effective): " + ", ".join(sorted(included_domains_effective)) + "\n")
    else:
      f.write("Included domains (effective): (all)\n")

    if include_domains_raw:
      f.write("include_domains (config): " + ", ".join(sorted({str(d).strip().lower() for d in include_domains_raw})) + "\n")
    else:
      f.write("include_domains (config): (empty => all)\n")

    f.write("Available domains: " + ", ".join(sorted(available_domains)) + "\n")

    # Statistiche filtro fisico
    if filter_stats:
      f.write("Physical filter stats:\n")
      for k, v in filter_stats.items():
        f.write(f"  {k}: {v}\n")

    # Warnings sui domini
    if domain_warnings:
      for w in domain_warnings:
        f.write("WARNING: " + w + "\n")

    f.write("\n")

    # Corpo del report
    for domain in sorted(grouped.keys()):
      entities = sorted(grouped[domain], key=lambda x: x.get("entity_id", ""))
      total = len(entities)
      f.write(f"=== DOMAIN: {domain} ({total}) ===\n")
      if max_entities and total > max_entities:
        entities = entities[:max_entities]
        f.write(f"(showing first {max_entities} entities)\n")

      for s in entities:
        for ln in _format_state_lines_all_attrs(s):
          f.write(ln + "\n")
        f.write("\n")

    f.write("===== END =====\n")

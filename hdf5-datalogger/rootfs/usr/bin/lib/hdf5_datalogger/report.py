import json
from .timeutils import utc_now_z

def _format_state_lines_all_attrs(state: dict) -> list:
    lines = []
    eid = state.get("entity_id", "unknown")
    st = state.get("state", "unknown")
    attrs = state.get("attributes", {}) or {}
    friendly = attrs.get("friendly_name")

    lines.append(f"- {eid}")
    lines.append(f"  state: {st}")
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
):
    ts = utc_now_z()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("===== HOME ASSISTANT STATES REPORT =====\n")
        f.write(f"Generated at: {ts}\n\n")

        if included_domains_effective:
            f.write("Included domains: " + ", ".join(sorted(included_domains_effective)) + "\n")
        else:
            f.write("Included domains: (all)\n")
        f.write("Available domains: " + ", ".join(sorted(available_domains)) + "\n\n")

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

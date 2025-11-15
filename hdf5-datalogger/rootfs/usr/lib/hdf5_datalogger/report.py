import json
from .timeutils import utc_now_z
from .constants import ESSENTIAL_ATTRS

def _format_entity_lines(state: dict, mode: str, attrs_include: list, attrs_exclude: list) -> list:
    """
    mode: all | essentials | custom | none
    """
    lines = []
    eid = state.get("entity_id", "unknown")
    st = state.get("state", "unknown")
    attrs = state.get("attributes", {}) or {}
    friendly = attrs.get("friendly_name")

    lines.append(f"- {eid}")
    lines.append(f"  state: {st}")
    if friendly:
        lines.append(f"  name: {friendly}")

    if mode == "none":
        return lines

    keys = set(attrs.keys()) - {"friendly_name"}

    # exclude "rumorosi" sempre applicato
    if attrs_exclude:
        keys -= set(attrs_exclude)

    if mode == "essentials":
        keys = keys & ESSENTIAL_ATTRS
    elif mode == "custom":
        wanted = {str(k).strip() for k in (attrs_include or []) if str(k).strip()}
        keys = keys & wanted
    else:  # "all"
        pass

    for key in sorted(keys):
        val = attrs.get(key)
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
    attributes_mode: str,
    attributes_include: list,
    attributes_exclude: list,
    domain_warnings: list,
):
    ts = utc_now_z()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("===== HOME ASSISTANT STATES REPORT =====\n")
        f.write(f"Generated at: {ts}\n\n")

        # Header informativo
        if included_domains_effective:
            f.write("Included domains: " + ", ".join(sorted(included_domains_effective)) + "\n")
        else:
            f.write("Included domains: (all)\n")
        f.write("Available domains: " + ", ".join(sorted(available_domains)) + "\n")
        f.write(f"Attributes mode: {attributes_mode}\n")
        if attributes_exclude:
            f.write("Attributes exclude: " + ", ".join(sorted(set(attributes_exclude))) + "\n")
        if attributes_mode == "custom" and attributes_include:
            f.write("Attributes include: " + ", ".join(sorted(set(str(x) for x in attributes_include))) + "\n")
        if domain_warnings:
            for w in domain_warnings:
                f.write("WARNING: " + w + "\n")
        f.write("\n")

        # Corpo
        for domain in sorted(grouped.keys()):
            entities = sorted(grouped[domain], key=lambda x: x.get("entity_id", ""))
            total = len(entities)
            f.write(f"=== DOMAIN: {domain} ({total}) ===\n")
            if max_entities and total > max_entities:
                entities = entities[:max_entities]
                f.write(f"(showing first {max_entities} entities)\n")

            for s in entities:
                for ln in _format_entity_lines(s, attributes_mode, attributes_include, attributes_exclude):
                    f.write(ln + "\n")
                f.write("\n")

        f.write("===== END =====\n")

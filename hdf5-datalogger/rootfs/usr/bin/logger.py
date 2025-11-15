#!/usr/bin/env python3
"""
HDF5 DataLogger - v0.2.0
- REST only: /api/states
- Domain filtering via boolean flags + include_domains_extra
- Text report, grouped by domain
- Logs ALL attributes for each entity
"""
import os
import json
from datetime import datetime, timezone
from collections import defaultdict

import requests

API_URL = "http://supervisor/core/api"
TOKEN = os.getenv("SUPERVISOR_TOKEN")
OPTIONS_PATH = "/data/options.json"

if not TOKEN:
    raise SystemExit(
        "ERROR: SUPERVISOR_TOKEN missing. Ensure homeassistant_api: true in config.yaml."
    )

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Mapping "flag option" -> domain
DOMAIN_FLAGS = {
    "include_sensor": "sensor",
    "include_binary_sensor": "binary_sensor",
    "include_light": "light",
    "include_switch": "switch",
    "include_climate": "climate",
    "include_cover": "cover",
    "include_fan": "fan",
    "include_media_player": "media_player",
    "include_lock": "lock",
    "include_device_tracker": "device_tracker",
    "include_person": "person",
    "include_camera": "camera",
    "include_alarm_control_panel": "alarm_control_panel",
    "include_scene": "scene",
    "include_script": "script",
    "include_automation": "automation",
    "include_button": "button",
    "include_number": "number",
    "include_select": "select",
    "include_input_boolean": "input_boolean",
    "include_input_number": "input_number",
    "include_input_select": "input_select",
    "include_input_text": "input_text",
    "include_vacuum": "vacuum",
    "include_weather": "weather",
    "include_water_heater": "water_heater",
    "include_valve": "valve",
    "include_siren": "siren",
}

def load_options():
    # Defaults aligned with config.yaml
    opts = {
        "output_path": "/share/example_addon_output.txt",
        "max_entities": 0,
        "include_domains_extra": [],
        # flags default values are handled by HA UI, but keep safe fallbacks here:
        **{k: False for k in DOMAIN_FLAGS.keys()},
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # copy known keys if present
        for k in opts.keys():
            if k in data:
                opts[k] = data[k]
    except Exception:
        pass
    return opts

def normalize_domain(d: str) -> str:
    """Basic normalization for extra domains input."""
    if not d:
        return ""
    d = d.strip().lower()
    # common plural -> singular corrections / typos
    corrections = {
        "sensors": "sensor",
        "binary_sensors": "binary_sensor",
        "lights": "light",
        "switches": "switch",
        "binanry_sensor": "binary_sensor",
        "binanry_sensors": "binary_sensor",
    }
    return corrections.get(d, d)

def build_included_domains(opts: dict, available_domains: set) -> set:
    """Build the final set of domains to include from flags + extras."""
    selected = set()

    # from boolean flags
    for flag, domain in DOMAIN_FLAGS.items():
        if opts.get(flag, False):
            selected.add(domain)

    # from extra list
    extras = opts.get("include_domains_extra", []) or []
    for d in extras:
        nd = normalize_domain(str(d))
        if nd:
            selected.add(nd)

    # If nothing selected, fallback to "include all"
    if not selected:
        return set()  # empty = include all

    # Keep only those that actually appear (helps avoid empty reports due to typos)
    if available_domains:
        return {d for d in selected if d in available_domains}
    return selected

def get_states():
    url = f"{API_URL}/states"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def domain_of(entity_id: str) -> str:
    return entity_id.split(".", 1)[0].lower() if "." in entity_id else "unknown"

def format_state_lines_all_attrs(s: dict) -> list:
    """Return lines for one entity, logging ALL attributes."""
    lines = []
    entity_id = s.get("entity_id", "unknown")
    state = s.get("state", "unknown")
    attrs = s.get("attributes", {}) or {}

    friendly = attrs.get("friendly_name")

    lines.append(f"- {entity_id}")
    lines.append(f"  state: {state}")
    if friendly:
        lines.append(f"  name: {friendly}")

    # Log ALL attributes (skip friendly_name to avoid duplicate)
    for key in sorted(attrs.keys()):
        if key == "friendly_name":
            continue
        val = attrs[key]
        # Serialize dict/list nicely on one line
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
    # timezone-aware UTC timestamp, with "Z"
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("===== HOME ASSISTANT STATES REPORT =====\n")
        f.write(f"Generated at: {ts}\n\n")

        # Debug/help header
        if included_domains_effective:
            f.write(
                "Included domains: "
                + ", ".join(sorted(included_domains_effective))
                + "\n"
            )
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
                for ln in format_state_lines_all_attrs(s):
                    f.write(ln + "\n")
                f.write("\n")

        f.write("===== END =====\n")

def main():
    opts = load_options()
    output_path = opts["output_path"]
    max_entities = int(opts.get("max_entities", 0) or 0)

    try:
        all_states = get_states()
    except Exception as e:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("===== HOME ASSISTANT STATES REPORT =====\n")
            f.write(f"Generated at: {ts}\n\n")
            f.write(f"ERROR fetching /states: {e}\n")
            f.write("===== END =====\n")
        return

    # discover domains present in the system
    available_domains = set()
    for s in all_states:
        eid = s.get("entity_id", "")
        available_domains.add(domain_of(eid))

    # Build final included domains set (flags + extra)
    selected_domains = build_included_domains(opts, available_domains)

    # Group states by domain, applying filter if any
    grouped = defaultdict(list)
    for s in all_states:
        d = domain_of(s.get("entity_id", ""))
        if selected_domains and d not in selected_domains:
            continue
        grouped[d].append(s)

    write_report(
        output_path=output_path,
        grouped=grouped,
        max_entities=max_entities,
        available_domains=available_domains,
        included_domains_effective=selected_domains,
    )

if __name__ == "__main__":
    main()

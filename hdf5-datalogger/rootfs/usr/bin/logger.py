#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from collections import defaultdict

API_URL = "http://supervisor/core/api"
TOKEN = os.getenv("SUPERVISOR_TOKEN")
OPTIONS_PATH = "/data/options.json"

if not TOKEN:
    raise SystemExit("ERROR: SUPERVISOR_TOKEN missing. Ensure homeassistant_api: true in config.yaml.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def load_options():
    # Valori di default
    opts = {
        "output_path": "/share/example_addon_output.txt",
        "include_domains": [],
        "include_attributes": [],
        "max_entities": 0,
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        opts.update({k: data.get(k, opts[k]) for k in opts.keys()})
    except Exception:
        pass
    return opts

def get_states():
    url = f"{API_URL}/states"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def domain_of(entity_id: str) -> str:
    return entity_id.split(".", 1)[0] if "." in entity_id else "unknown"

def should_include_domain(domain: str, include_domains: list) -> bool:
    if not include_domains:
        return True  # nessun filtro => includi tutti
    return domain in include_domains

def format_state_line(s: dict, include_attrs: list) -> list:
    lines = []
    entity_id = s.get("entity_id", "unknown")
    state = s.get("state", "unknown")
    attrs = s.get("attributes", {}) or {}

    friendly = attrs.get("friendly_name")
    lines.append(f"- {entity_id}")
    lines.append(f"  state: {state}")
    if friendly:
        lines.append(f"  name: {friendly}")

    # Attributi extra richiesti
    for key in include_attrs:
        if key in attrs:
            val = attrs.get(key)
            lines.append(f"  {key}: {val}")
    return lines

def write_report(output_path: str, grouped: dict, include_attrs: list, max_entities: int):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("===== HOME ASSISTANT STATES REPORT =====\n")
        f.write(f"Generated at: {datetime.utcnow().isoformat()}Z\n\n")

        for domain in sorted(grouped.keys()):
            entities = sorted(grouped[domain], key=lambda x: x.get("entity_id",""))
            total = len(entities)
            f.write(f"=== DOMAIN: {domain} ({total}) ===\n")
            if max_entities and total > max_entities:
                entities = entities[:max_entities]
                f.write(f"(showing first {max_entities} entities)\n")

            for s in entities:
                lines = format_state_line(s, include_attrs)
                for ln in lines:
                    f.write(ln + "\n")
                f.write("\n")

        f.write("===== END =====\n")

def main():
    opts = load_options()
    output_path = opts["output_path"]
    include_domains = opts["include_domains"]
    include_attrs = opts["include_attributes"]
    max_entities = opts["max_entities"]

    try:
        all_states = get_states()
    except Exception as e:
        # In caso di errore rete/auth, lascia un messaggio semplice nel file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("===== HOME ASSISTANT STATES REPORT =====\n")
            f.write(f"Generated at: {datetime.utcnow().isoformat()}Z\n\n")
            f.write(f"ERROR fetching /states: {e}\n")
            f.write("===== END =====\n")
        return

    grouped = defaultdict(list)
    for s in all_states:
        eid = s.get("entity_id", "")
        d = domain_of(eid)
        if should_include_domain(d, include_domains):
            grouped[d].append(s)

    write_report(output_path, grouped, include_attrs, max_entities)

if __name__ == "__main__":
    main()

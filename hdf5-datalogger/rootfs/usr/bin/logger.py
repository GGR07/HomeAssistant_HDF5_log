#!/usr/bin/env python3
"""
HDF5 DataLogger - v0.3.0
- REST /api/states
- Domini: presets | custom | all + exclude + strict
- Attributi: all | essentials | custom | none (+ exclude)
"""
import os
import sys

# fallback PYTHONPATH se il run non lo esporta
if "/usr/lib" not in sys.path:
    sys.path.insert(0, "/usr/lib")

from hdf5_datalogger.config_loader import load_options
from hdf5_datalogger.ha_client import get_states
from hdf5_datalogger.domains import (
    discover_available_domains,
    build_domains_from_options,
    group_states_by_domain,
)
from hdf5_datalogger.report import write_report
from hdf5_datalogger.timeutils import utc_now_z

TOKEN = os.getenv("SUPERVISOR_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: SUPERVISOR_TOKEN missing. Ensure homeassistant_api: true.")

def main():
    opts = load_options()
    output_path = opts["output_path"]
    max_entities = int(opts.get("max_entities", 0) or 0)

    try:
        all_states = get_states(TOKEN)
    except Exception as e:
        ts = utc_now_z()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("===== HOME ASSISTANT STATES REPORT =====\n")
            f.write(f"Generated at: {ts}\n\n")
            f.write(f"ERROR fetching /states: {e}\n")
            f.write("===== END =====\n")
        return

    available_domains = discover_available_domains(all_states)
    selected_domains, domain_warnings = build_domains_from_options(opts, available_domains)
    grouped = group_states_by_domain(all_states, selected_domains)

    write_report(
        output_path=output_path,
        grouped=grouped,
        max_entities=max_entities,
        available_domains=available_domains,
        included_domains_effective=selected_domains,
        attributes_mode=(opts.get("attributes_mode") or "all"),
        attributes_include=opts.get("attributes_include") or [],
        attributes_exclude=opts.get("attributes_exclude") or [],
        domain_warnings=domain_warnings,
    )

if __name__ == "__main__":
    main()
